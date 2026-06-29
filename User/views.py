import json
import random
from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from User.models import *

# ====================================
# Login Page View
# ====================================
class LoginPageView(TemplateView):
    template_name = "login.html"

class SignupPageView(TemplateView):
    template_name = "signup.html"
    
# ====================================
# Send OTP View
# ====================================
class SendOTPView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        phone = data.get('phone', '').strip()
        is_signup = data.get('is_signup', False)

        if not username or not email:
            return JsonResponse({"status": "error", "message": "Username and Email are required"}, status=400)

        # ==================================================================
        # ૧. HANDLE FRESH REGISTRATION FLOW 
        # ==================================================================
        if is_signup:
            if User.objects.filter(username=username).exists():
                return JsonResponse({"status": "error", "message": "Username is already taken"}, status=400)
            if User.objects.filter(email=email).exists():
                return JsonResponse({"status": "error", "message": "Email is already registered"}, status=400)

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = phone
            profile.save()

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(
                username=username,
                email=email,
                otp=otp_code
            )

            print(f"=== SECURITY LOG: SIGNUP OTP FOR [{username}] IS {otp_code} ===")

            return JsonResponse({
                "status": "success",
                "message": "Account created successfully! Proceeding to Verification.",
                "otp": otp_code  
            })

        # ==================================================================
        # ૨. HANDLE STANDARD LOGIN VERIFICATION REQUEST 
        # ==================================================================
        else:
            try:
                user = User.objects.get(username=username, email=email)
            except User.DoesNotExist:
                return JsonResponse({
                    "status": "error", 
                    "message": "Account not found. Please signup first!"
                }, status=400) 

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(
                username=username,
                email=email,
                otp=otp_code
            )

            print(f"=== SECURITY LOG: LOGIN OTP FOR [{username}] IS {otp_code} ===")

            return JsonResponse({
                "status": "success",
                "message": "OTP sent successfully",
                "otp": otp_code
            })

# ====================================
# VERIFY OTP VIEW (PERFORMS SESSION LOGIN)
# ====================================
class VerifyOTPView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)

        email = data.get('email', '').strip()
        otp = data.get('otp', '').strip()

        if not email or not otp:
            return JsonResponse({"status": "error", "message": "All fields are required"}, status=400)

        record = OTP.objects.filter(email=email).last()

        if not record:
            return JsonResponse({"status": "error", "message": "OTP record not found"}, status=404)

        if record.is_expired():
            return JsonResponse({"status": "error", "message": "OTP has expired"}, status=400)

        if record.otp != otp:
            return JsonResponse({"status": "error", "message": "Invalid OTP code provided"}, status=400)

        user = User.objects.get(username=record.username)
        login(request, user)
        messages.success(request, "Logged in successfully")
        
        if user.is_staff or user.is_superuser:
            redirect_url = "/dashboard/settings/"
        else:
            redirect_url = "/"

        return JsonResponse({
            "status": "success",
            "message": "Login successful",
            "redirect_url": redirect_url
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
# PROFILE API VIEW
# ====================================

class ProfileAPI(View):

    def get(self, request):

        if not request.user.is_authenticated:

            return JsonResponse({
                "error": "Login required"
            }, status=401)

        user = request.user

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        return JsonResponse({

            "username": user.username,

            "email": user.email,

            "first_name": user.first_name,

            "last_name": user.last_name,

            "phone": profile.phone,

            "city": profile.city,

            "bio": profile.bio,

            "image": (
                profile.image.url
                if profile.image
                else ""
            )

        })

    def post(self, request):

        return self.update_user(request)

    def put(self, request):

        return self.update_user(request)

    def update_user(self, request):

        if not request.user.is_authenticated:

            return JsonResponse({
                "error": "Login required"
            }, status=401)

        try:

            data = json.loads(request.body)

        except:

            return JsonResponse({
                "error": "Invalid JSON"
            }, status=400)

        user = request.user

        # USERNAME

        if "username" in data:

            if not data["username"]:

                return JsonResponse({

                    "username": [
                        "Username required"
                    ]

                }, status=400)

            user.username = data["username"]

        # EMAIL

        if "email" in data:

            if (
                data["email"]
                and "@"
                not in data["email"]
            ):

                return JsonResponse({

                    "email": [
                        "Invalid email"
                    ]

                }, status=400)

            user.email = data["email"]

        # FIRST NAME

        if "first_name" in data:

            user.first_name = data["first_name"]

        # LAST NAME

        if "last_name" in data:

            user.last_name = data["last_name"]

        user.save()

        # PROFILE

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        if "phone" in data:

            profile.phone = data["phone"]

        if "city" in data:

            profile.city = data["city"]

        if "bio" in data:

            profile.bio = data["bio"]

        profile.save()

        return JsonResponse({
            "status": "success"
        })


# ====================================
# PROFILE VIEW
# ====================================

class ProfileView(
    LoginRequiredMixin,
    TemplateView
):

    template_name = "profile.html"

    def get_context_data(
        self,
        **kwargs
    ):

        context = super().get_context_data(
            **kwargs
        )

        # PROFILE

        profile, created = Profile.objects.get_or_create(
            user=self.request.user
        )

        context["profile"] = profile

        # WISHLIST

        context["wishlist_items"] = Wishlist.objects.filter(
            user=self.request.user
        ).select_related("product")

        # CART

        cart, created = Cart.objects.get_or_create(
            user=self.request.user
        )

        context["cart_items"] = CartItem.objects.filter(
            cart=cart
        ).select_related("product")

        # CART PRODUCT IDS

        context["cart_product_ids"] = CartItem.objects.filter(
            cart__user=self.request.user
        ).values_list(
            "product_id",
            flat=True
        )

        # ORDERS

        context["orders"] = Order.objects.filter(
            user=self.request.user
        ).order_by("-id")

        # ADDRESS

        context["addresses"] = Address.objects.filter(
            user=self.request.user
        ).order_by("-id")
        context["used_coupons"] = Order.objects.filter(
            user=self.request.user
        ).exclude(
            earned_coupons=None
        ).order_by("-id").prefetch_related('items__product')
        return context

# ====================================
# UPLOAD IMAGE VIEW
# ====================================

class UploadImageView(View):

    def post(self, request):

        if not request.user.is_authenticated:

            return JsonResponse({
                "error": "Login required"
            }, status=403)

        image = request.FILES.get("image")

        if not image:

            return JsonResponse({
                "error": "No image"
            }, status=400)

        profile, created = Profile.objects.get_or_create(
            user=request.user
        )

        profile.image = image

        profile.save()

        return JsonResponse({

            "status": "success",

            "image": profile.image.url

        })
        
# ====================================
# ADD ADDRESS
# ====================================

class AddAddressView(LoginRequiredMixin, View):

    def post(self, request):

        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not full_name:
            return JsonResponse({
                "error": "Full name is required"
            }, status=400)

        if not phone:
            return JsonResponse({
                "error": "Phone number is required"
            }, status=400)

        if not phone.isdigit() or len(phone) != 10:
            return JsonResponse({
                "error": "Phone number must be 10 digits"
            }, status=400)

        if not address:
            return JsonResponse({
                "error": "Address is required"
            }, status=400)

        if not city:
            return JsonResponse({
                "error": "City is required"
            }, status=400)

        if not state:
            return JsonResponse({
                "error": "State is required"
            }, status=400)

        if not pincode:
            return JsonResponse({
                "error": "Pincode is required"
            }, status=400)

        if not pincode.isdigit() or len(pincode) != 6:
            return JsonResponse({
                "error": "Invalid pincode"
            }, status=400)

        Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode
        )

        return JsonResponse({
            "success": True,
            "message": "Address added successfully"
        })


# ====================================
# DELETE ADDRESS
# ====================================

class DeleteAddressView(LoginRequiredMixin, View):

    def post(self, request, id):

        address = get_object_or_404(
            Address,
            id=id,
            user=request.user
        )

        address.delete()

        return JsonResponse({
            "success": True,
            "message": "Address deleted successfully"
        })
        
class SetDefaultAddressView(LoginRequiredMixin, View):

    def post(self, request, id):

        try:

            address = Address.objects.get(
                id=id,
                user=request.user
            )

            Address.objects.filter(
                user=request.user
            ).update(is_default=False)

            address.is_default = True
            address.save()

            return JsonResponse({
                "status": "success"
            })

        except Address.DoesNotExist:

            return JsonResponse({
                "status": "error",
                "message": "Address not found"
            })
            
class IndexView(TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()

        context['products'] = Product.objects.filter(
            is_featured=False
        ).prefetch_related("images", "colors", "sizes").all()

        # =========================
        # DEFAULTS
        # =========================
        featured_products = Product.objects.filter(
            is_featured=True
        ).prefetch_related("images", "colors", "sizes").order_by("-id")[:8]
        
        wishlist_product_ids = []
        wishlist_count = 0
        cart_product_ids = []
        cart_count = 0

        # =========================
        # USER LOGIN
        # =========================
        if self.request.user.is_authenticated:
            # WISHLIST
            wishlist_items = Wishlist.objects.filter(user=self.request.user)
            wishlist_product_ids = list(wishlist_items.values_list("product_id", flat=True))
            wishlist_count = wishlist_items.count()

            # CART
            cart, created = Cart.objects.get_or_create(user=self.request.user)
            cart_items = CartItem.objects.filter(cart=cart)
            cart_product_ids = list(cart_items.values_list("product_id", flat=True))
            cart_count = cart_items.count()

        # =========================
        # CONTEXT
        # =========================
        context["wishlist_product_ids"] = wishlist_product_ids
        context["wishlist_count"] = wishlist_count
        context["cart_product_ids"] = cart_product_ids
        context["cart_count"] = cart_count
        context["featured_products"] = featured_products

        return context
    
class contactview(TemplateView):
    template_name = 'contact.html'