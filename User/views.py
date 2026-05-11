from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login
from .models import *
from .serializers import *
from django.contrib.auth import logout
import json
import random
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import OTP

class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['products'] = Product.objects.all()

        return context

class shopview(TemplateView):
    template_name = "shop.html"
    
class detailview(TemplateView):
    template_name = 'detail.html'
    
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import Product


class ProductDetailView(View):

    def get(self, request, id):

        product = get_object_or_404(Product, id=id)

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:8]

        context = {
            "product": product,
            "related_products": related_products
        }

        return render(request, "detail.html", context)

class contactview(TemplateView):
    template_name = 'contact.html'
    
class cartview(TemplateView):
    template_name = 'cart.html'
    
class checkoutview(TemplateView):
    template_name = 'checkout.html'
    
    
# ====================================== 
# Dashboard Views 
# ====================================== 
    
class Dashboardview(TemplateView):
    template_name = 'dashboard/index.html'
    
#  GET Categories
class CategoryListAPI(APIView):
    def get(self, request):
        data = Category.objects.all()
        serializer = CategorySerializer(data, many=True)
        return Response(serializer.data)


#  GET Types by Category
class TypeListAPI(APIView):
    def get(self, request, category_id):
        data = ProductType.objects.filter(category_id=category_id)
        serializer = ProductTypeSerializer(data, many=True)
        return Response(serializer.data)


#  CREATE Product
class ProductCreateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data)

            if serializer.is_valid():
                product = serializer.save()

                images = request.FILES.getlist('images')

                print("FILES:", images)   #  DEBUG

                for img in images:
                    ProductImage.objects.create(product=product, image=img)

                return Response({"message": "Product added"}, status=201)

            print(serializer.errors)  #  DEBUG
            return Response(serializer.errors, status=400)

        except Exception as e:
            print("ERROR:", str(e))
            return Response({"error": str(e)}, status=500)


class AddProductPageView(TemplateView):
    template_name = "dashboard/add_product.html"
    
#  ADD CATEGORY
class CategoryCreateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]  #  MUST

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Category added"}, status=201)

        return Response({"status": "error", "errors": serializer.errors}, status=400)


#  ADD TYPE
class ProductTypeCreateAPI(APIView):
    def post(self, request):
        serializer = ProductTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Type added"}, status=201)
        return Response(serializer.errors, status=400)

    
class AddCategoryPageView(TemplateView):
    template_name = "dashboard/add_category.html"
    
class AddTypePageView(TemplateView):
    template_name = "dashboard/add_type.html"
    
# GET ALL PRODUCTS
class ProductListAPI(APIView):
    def get(self, request):

        products = Product.objects.all().order_by('-id')

        return Response([
            {
                "id": p.id,
                "name": p.name,
                "price": p.price,
                "mrp": p.mrp,
                "discount": p.discount,
                "final_price": p.final_price(),
                "discount_percent": p.discount_percent(),
                "stock": p.stock,
                "category_name": p.category.name,
                "type_name": p.type.name,
                "images": [
                    {"image": img.image.url} for img in p.images.all()
                ]
            }
            for p in products
        ])
    
class ProductlistView(TemplateView):
    template_name = "dashboard/product_list.html"

class AuthPageView(TemplateView):
    template_name = "login.html"
    

# SEND OTP
class SendOTPView(View):

    def post(self, request):
        data = json.loads(request.body)
        username = data.get('username')
        email = data.get('email')

        if not username or not email:
                    return JsonResponse({
                        "status": "error",
                        "message": "Username and Email required"
                    })


        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(username=username,email=email, otp=otp_code)

        print("OTP:", otp_code) 

        return JsonResponse({
            "status": "success",
            "message": "OTP sent successfully"
        })


# VERIFY OTP
class VerifyOTPView(View):

    def post(self, request):
        data = json.loads(request.body)

        email = data.get('email')
        otp = data.get('otp')

        if not email or not otp:
            return JsonResponse({"status": "error", "message": "All fields required"})

        record = OTP.objects.filter(email=email).last()

        if not record:
            return JsonResponse({"status": "error", "message": "OTP not found"})

        if record.is_expired():
            return JsonResponse({"status": "error", "message": "OTP expired"})

        if record.otp != otp:
            return JsonResponse({"status": "error", "message": "Invalid OTP"})

        user, created = User.objects.get_or_create(
            username=record.username,      
            defaults={'email': record.email}
        )

        login(request, user)

        return JsonResponse({
            "status": "success",
            "message": "Login successful"
        })
        
class LogoutView(View):
    def post(self, request):
        logout(request)
        return JsonResponse({"status": "success"})
    
from django.views import View
from django.http import JsonResponse
import json

class ProfileAPI(View):

    def get(self, request):

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)

        return JsonResponse({
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": profile.phone,
            "city": profile.city,
            "bio": profile.bio,
            "image": profile.image.url if profile.image else ""
        })


    def post(self, request):
        return self.update_user(request)

    def put(self, request):
        return self.update_user(request)

    def update_user(self, request):

        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=401)

        try:
            data = json.loads(request.body)
        except:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        user = request.user

        # USER fields
        if "username" in data:
            if not data["username"]:
                return JsonResponse({"username": ["Username required"]}, status=400)
            user.username = data["username"]

        if "email" in data:
            if data["email"] and "@" not in data["email"]:
                return JsonResponse({"email": ["Invalid email"]}, status=400)
            user.email = data["email"]

        if "first_name" in data:
            user.first_name = data["first_name"]

        if "last_name" in data:
            user.last_name = data["last_name"]

        user.save()

        # ✅ PROFILE PART (VERY IMPORTANT 🔥🔥)
        profile, created = Profile.objects.get_or_create(user=user)

        if "phone" in data:
            profile.phone = data["phone"]

        if "city" in data:
            profile.city = data["city"]

        if "bio" in data:
            profile.bio = data["bio"]

        profile.save()

        return JsonResponse({"status": "success"})
    
class ProfilePageView(TemplateView):
    template_name = "profile.html"
    
from django.views import View
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin

class UploadImageView(View):
    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Login required"}, status=403)

        image = request.FILES.get("image")

        if not image:
            return JsonResponse({"error": "No image"}, status=400)

        profile, created = Profile.objects.get_or_create(user=request.user)

        profile.image = image  
        profile.save()         

        return JsonResponse({
            "image": profile.image.url
        })