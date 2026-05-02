from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import authenticate, login
from .models import *
from .serializers import *

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

            if serializers.is_valid():
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
    
# views.py
import json, random
from django.http import JsonResponse
from django.views import View
from .models import OTP


class SendOTPView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({"status": "error", "message": "Email required"})

            otp_code = str(random.randint(100000, 999999))

            OTP.objects.create(email=email, otp=otp_code)

            print("OTP:", otp_code)  # dev mate

            return JsonResponse({"status": "success", "message": "OTP sent"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        
from django.contrib.auth.models import User
from django.contrib.auth import login


class VerifyOTPView(View):

    def post(self, request):
        try:
            data = json.loads(request.body)

            email = data.get('email')
            otp = data.get('otp')

            if not email or not otp:
                return JsonResponse({"status": "error", "message": "All fields required"})

            record = OTP.objects.filter(email=email, otp=otp).last()

            if record and not record.is_expired():

                # 🔥 Auto create user (IMPORTANT)
                user, created = User.objects.get_or_create(username=email)

                login(request, user)  # session login

                return JsonResponse({
                    "status": "success",
                    "message": "Login successful"
                })

            return JsonResponse({"status": "error", "message": "Invalid or expired OTP"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})