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

            # remove old default address
            Address.objects.filter(
                user=request.user
            ).update(is_default=False)

            # set new default
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
        ).prefetch_related(
            "images"
        )

        # =========================
        # DEFAULTS
        # =========================
        featured_products = Product.objects.filter(
            is_featured=True
        ).order_by("-id")[:8]
        
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
        
        context["featured_products"] = featured_products

        return context
    
class contactview(TemplateView):
    template_name = 'contact.html'