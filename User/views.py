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
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import OTP
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.shortcuts import render, get_object_or_404

from django.http import JsonResponse
from django.views.generic import View

from .models import Product


class SearchProductView(View):

    def get(self, request, *args, **kwargs):

        search = request.GET.get("search", "")

        products = Product.objects.filter(
            name__icontains=search
        )[:8]

        product_list = []

        for product in products:

            # GET FIRST IMAGE
            first_image = product.images.first()

            # IMAGE URL
            if first_image and first_image.image:
                image_url = first_image.image.url
            else:
                image_url = "/static/img/no-image.png"

            product_list.append({

                "id": product.id,

                "name": product.name,

                "price": str(product.price),

                "image": image_url,

            })

        return JsonResponse({

            "products": product_list

        })
# =========================
# INDEX VIEW
# =========================

class IndexView(TemplateView):

    template_name = "index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()

        context['products'] = Product.objects.all().prefetch_related(
            "images"
        )

        # =========================
        # DEFAULTS
        # =========================

        wishlist_product_ids = []

        wishlist_count = 0

        cart_product_ids = []

        cart_count = 0


        # =========================
        # USER LOGIN
        # =========================

        if self.request.user.is_authenticated:

            # WISHLIST

            wishlist_items = Wishlist.objects.filter(
                user=self.request.user
            )

            wishlist_product_ids = list(

                wishlist_items.values_list(
                    "product_id",
                    flat=True
                )

            )

            wishlist_count = wishlist_items.count()


            # CART

            cart, created = Cart.objects.get_or_create(
                user=self.request.user
            )

            cart_items = CartItem.objects.filter(
                cart=cart
            )

            cart_product_ids = list(

                cart_items.values_list(
                    "product_id",
                    flat=True
                )

            )

            cart_count = cart_items.count()


        # =========================
        # CONTEXT
        # =========================

        context["wishlist_product_ids"] = wishlist_product_ids

        context["wishlist_count"] = wishlist_count

        context["cart_product_ids"] = cart_product_ids

        context["cart_count"] = cart_count

        return context
    
# ====================================
# Shop View
# ====================================
class shopview(TemplateView):
    template_name = "shop.html"
    
# ====================================
# Detail View
# ====================================
from .models import Wishlist
from .models import CartItem
from .models import Cart


class detailview(TemplateView):

    template_name = "detail.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        product = Product.objects.get(
            id=self.kwargs["pk"]
        )

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        )[:8]

        # MAIN PRODUCT CART
        in_cart = False

        # MAIN PRODUCT WISHLIST
        in_wishlist = False

        # RELATED PRODUCTS
        cart_product_ids = []
        wishlist_product_ids = []

        if self.request.user.is_authenticated:

            # CART
            cart = Cart.objects.filter(
                user=self.request.user
            ).first()

            if cart:

                cart_product_ids = list(

                    CartItem.objects.filter(
                        cart=cart
                    ).values_list(
                        "product_id",
                        flat=True
                    )

                )

                in_cart = product.id in cart_product_ids

            # WISHLIST
            wishlist_product_ids = list(

                Wishlist.objects.filter(
                    user=self.request.user
                ).values_list(
                    "product_id",
                    flat=True
                )

            )

            in_wishlist = product.id in wishlist_product_ids

        context["product"] = product

        context["related_products"] = related_products

        context["in_cart"] = in_cart

        context["in_wishlist"] = in_wishlist

        context["cart_product_ids"] = cart_product_ids

        context["wishlist_product_ids"] = wishlist_product_ids

        return context

# ====================================
# Product Detail View
# ====================================
class ProductDetailView(View):

    def get(self, request, id):

        product = get_object_or_404(
            Product,
            id=id
        )

        related_products = Product.objects.filter(
            category=product.category
        ).exclude(
            id=product.id
        )[:8]

        # =========================
        # CHECK PRODUCT IN CART
        # =========================

        in_cart = False

        if request.user.is_authenticated:

            in_cart = CartItem.objects.filter(

                cart__user=request.user,

                product=product

            ).exists()

        context = {

            "product": product,

            "related_products": related_products,

            "in_cart": in_cart

        }

        return render(
            request,
            "detail.html",
            context
        )
    
# ====================================
# Contact View
# ====================================
class contactview(TemplateView):
    template_name = 'contact.html'
    
# ====================================
# Cart View
# ====================================
# class cartview(TemplateView):
#     template_name = 'cart.html'
    
# ==================================== 
# CheckOut View 
# ==================================== 
class checkoutview(TemplateView):
    template_name = 'checkout.html'
    
# ====================================== 
# Dashboard Views 
# ====================================== 
class Dashboardview(TemplateView):
    template_name = 'dashboard/index.html'
    
# ====================================
# Category LIst API View
# ====================================
class CategoryListAPI(APIView):
    def get(self, request):
        data = Category.objects.all()
        serializer = CategorySerializer(data, many=True)
        return Response(serializer.data)

# ====================================
# Type List API View
# ====================================
class TypeListAPI(APIView):
    def get(self, request, category_id):
        data = ProductType.objects.filter(category_id=category_id)
        serializer = ProductTypeSerializer(data, many=True)
        return Response(serializer.data)

# ====================================
# Product Create API View
# ====================================
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

# ====================================
# Add Product Page View
# ====================================
class AddProductPageView(TemplateView):
    template_name = "dashboard/add_product.html"
    
# ====================================
# Category Create API View
# ====================================
class CategoryCreateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]  #  MUST

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Category added"}, status=201)

        return Response({"status": "error", "errors": serializer.errors}, status=400)

# ====================================
# Product Type Create API View 
# ====================================
class ProductTypeCreateAPI(APIView):
    def post(self, request):
        serializer = ProductTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Type added"}, status=201)
        return Response(serializer.errors, status=400)

# ==================================== 
# Add Category Page View 
# ==================================== 
class AddCategoryPageView(TemplateView):
    template_name = "dashboard/add_category.html"
    
# ==================================== 
# Add Type Page View 
# ==================================== 
class AddTypePageView(TemplateView):
    template_name = "dashboard/add_type.html"
    
# ====================================
# Product List API View
# ====================================
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
    
# ==================================== 
# Product List View 
# ==================================== 
class ProductlistView(TemplateView):
    template_name = "dashboard/product_list.html"

# ====================================
# Login Page View
# ====================================
class LoginPageView(TemplateView):
    template_name = "login.html"
    
# ====================================
# Send OTP View
# ====================================
class SendOTPView(View):

    def post(self, request):

        data = json.loads(request.body)

        username = data.get('username')

        email = data.get('email')

        # REQUIRED
        if not username or not email:

            return JsonResponse({

                "status": "error",

                "message": "Username and Email required"

            })

        # GENERATE OTP
        otp_code = str(random.randint(100000, 999999))

        # SAVE OTP
        OTP.objects.create(

            username=username,

            email=email,

            otp=otp_code

        )

        # RETURN OTP
        return JsonResponse({

            "status": "success",

            "message": "OTP sent successfully",

            "otp": otp_code

        })

# ====================================
# Verify OTP View
# ====================================
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

        messages.success(request, "Login Successfully")
        
        return JsonResponse({
            "status": "success",
            "message": "Login successful"
        })
        
# ==================================== 
# Logout View 
# ==================================== 
class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.success(request, "Logout Successfully")
        return JsonResponse({"status": "success"})
    
# ==================================== 
# Profile API View 
# ==================================== 
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

        profile, created = Profile.objects.get_or_create(user=user)

        if "phone" in data:
            profile.phone = data["phone"]

        if "city" in data:
            profile.city = data["city"]

        if "bio" in data:
            profile.bio = data["bio"]

        profile.save()

        return JsonResponse({"status": "success"})
    
# ====================================
# Profile Page View
# ====================================
class ProfilePageView(TemplateView):
    template_name = "profile.html"
    
# ====================================
# Upload Image View
# ====================================
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
        
# ====================================
# Wishlist API View
# ====================================
class WishlistAPIView(LoginRequiredMixin, View):

    def post(self, request):

        product_id = request.POST.get("product_id")

        if not product_id:
            return JsonResponse({
                "status": "error",
                "message": "Product id required"
            })

        try:
            product = Product.objects.get(id=product_id)

        except Product.DoesNotExist:
            return JsonResponse({
                "status": "error",
                "message": "Product not found"
            })

        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            product=product
        ).first()

        # REMOVE
        if wishlist_item:

            wishlist_item.delete()

            cache_key = f"wishlist_{request.user.id}"
            cache.delete(cache_key)

            wishlist_count = Wishlist.objects.filter(
                user=request.user
            ).count()

            return JsonResponse({
                "status": "removed",
                "wishlist_count": wishlist_count
            })

        # ADD
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

        cache_key = f"wishlist_{request.user.id}"
        cache.delete(cache_key)

        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

        return JsonResponse({
            "status": "added",
            "wishlist_count": wishlist_count
        })

# ====================================
# Wishlist Data API View
# ====================================
class WishlistDataAPIView(LoginRequiredMixin, View):

    def get(self, request):

        cache_key = f"wishlist_{request.user.id}"

        cached_data = cache.get(cache_key)

        # RETURN CACHE DATA
        if cached_data:
            return JsonResponse({
                "cached": True,
                "wishlist": cached_data
            })

        wishlist_items = Wishlist.objects.filter(
            user=request.user
        ).select_related("product")

        data = []

        for item in wishlist_items:

            data.append({
                "id": item.product.id,
                "name": item.product.name,
                "price": str(item.product.price),
            })

        # STORE CACHE FOR 5 MINUTES
        cache.set(cache_key, data, timeout=300)

        return JsonResponse({
            "cached": False,
            "wishlist": data
        })
        
# ====================================
# Wishlist Page View
# ====================================

class WishlistPageView(TemplateView):

    template_name = "wishlist.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:

            wishlist_items = Wishlist.objects.filter(
                user=self.request.user
            ).select_related(
                "product"
            ).prefetch_related(
                "product__images"
            )

            wishlist_data = []

            for item in wishlist_items:

                product = item.product

                # =========================
                # CHECK CART
                # =========================

                in_cart = CartItem.objects.filter(
                    cart__user=self.request.user,
                    product=product
                ).exists()

                wishlist_data.append({

                    "id": product.id,

                    "name": product.name,

                    "price": product.price,

                    "final_price": product.final_price(),

                    "discount": product.discount,

                    "discount_percent":
                    product.discount_percent(),

                    "image":
                    product.images.first().image.url
                    if product.images.first()
                    else "",

                    "in_cart": in_cart

                })

            context["wishlist_items"] = wishlist_data

            context["wishlist_count"] = len(
                wishlist_data
            )

        else:

            context["wishlist_items"] = []

            context["wishlist_count"] = 0

        return context
    
import json

from django.views.generic import TemplateView
from django.views import View

from django.http import JsonResponse

from django.shortcuts import get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin


from .models import Cart
from .models import CartItem
from .models import Product


# =========================================
# CART PAGE
# =========================================

class CartView(LoginRequiredMixin, TemplateView):

    template_name = "cart.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )

        cart_items = CartItem.objects.filter(
            cart=cart
        ).select_related(
            "product"
        )

        subtotal = sum(
            item.total_price for item in cart_items
        )

        shipping = 100 if subtotal > 0 else 0

        grand_total = subtotal + shipping

        context["cart_items"] = cart_items
        context["subtotal"] = subtotal
        context["shipping"] = shipping
        context["grand_total"] = grand_total

        return context


# =========================================
# ADD TO CART
# =========================================

class AddToCartView(LoginRequiredMixin, View):

    def post(self, request, product_id):

        product = get_object_or_404(
            Product,
            id=product_id
        )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        # REMOVE
        if cart_item:

            cart_item.delete()

            cart_count = CartItem.objects.filter(
                cart=cart
            ).count()

            return JsonResponse({

                "status": "removed",
                "cart_count": cart_count

            })

        # ADD
        CartItem.objects.create(

            cart=cart,
            product=product,
            quantity=1

        )

        cart_count = CartItem.objects.filter(
            cart=cart
        ).count()

        return JsonResponse({

            "status": "added",
            "cart_count": cart_count

        })

# =========================================
# UPDATE CART
# =========================================

class UpdateCartView(LoginRequiredMixin, View):

    def post(self, request, cart_id):

        data = json.loads(request.body)

        action = data.get("action")

        cart_item = get_object_or_404(

            CartItem,

            id=cart_id,

            cart__user=request.user

        )

        if action == "increase":

            cart_item.quantity += 1

            cart_item.save()

        elif action == "decrease":

            if cart_item.quantity > 1:

                cart_item.quantity -= 1

                cart_item.save()

            else:

                cart_item.delete()


                return JsonResponse({

                    "success": True

                })

        return JsonResponse({

            "success": True

        })


# =========================================
# REMOVE CART
# =========================================

class RemoveCartView(LoginRequiredMixin, View):

    def post(self, request, cart_id):

        cart_item = get_object_or_404(

            CartItem,

            id=cart_id,

            cart__user=request.user

        )

        cart_item.delete()

        return JsonResponse({

            "success": True,
            "message": "Removed"

        })