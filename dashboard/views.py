from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import (TemplateView,ListView,DeleteView,DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from rest_framework import generics
from User.models import *
from User.serializers import *
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
import json
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework import status
from dashboard.serializers import OrderSerializer
from django.utils.timezone import now
from datetime import timedelta
from django.utils.dateparse import parse_date
from django.contrib import messages
from dashboard.serializers import CouponSerializer
from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from django.contrib.auth import authenticate
from .serializers import DashboardLoginSerializer

# ====================================
# Dashboard View
# ====================================
class Dashboardview(TemplateView):

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # =========================
        # TOTAL COUNTS
        # =========================

        context['total_users'] = User.objects.count()

        context['total_orders'] = Order.objects.count()

        context['total_products'] = Product.objects.count()

        # =========================
        # USER GROWTH
        # =========================

        current_date = now()

        current_month_users = User.objects.filter(
            date_joined__month=current_date.month,
            date_joined__year=current_date.year
        ).count()

        first_day_current_month = current_date.replace(day=1)

        last_month_date = first_day_current_month - timedelta(days=1)

        last_month_users = User.objects.filter(
            date_joined__month=last_month_date.month,
            date_joined__year=last_month_date.year
        ).count()

        if last_month_users > 0:

            user_growth = round(
                (
                    (
                        current_month_users - last_month_users
                    ) / last_month_users
                ) * 100
            )

        else:

            user_growth = 100 if current_month_users > 0 else 0

        context['user_growth'] = user_growth

        # =========================
        # ORDER GROWTH
        # =========================

        current_month_orders = Order.objects.filter(
            created_at__month=current_date.month,
            created_at__year=current_date.year
        ).count()

        last_month_orders = Order.objects.filter(
            created_at__month=last_month_date.month,
            created_at__year=last_month_date.year
        ).count()

        if last_month_orders > 0:

            order_growth = round(
                (
                    (
                        current_month_orders - last_month_orders
                    ) / last_month_orders
                ) * 100
            )

        else:

            order_growth = 100 if current_month_orders > 0 else 0

        context['order_growth'] = order_growth

        # =========================
        # PRODUCT GROWTH
        # =========================

        current_month_products = Product.objects.filter(
            created_at__month=current_date.month,
            created_at__year=current_date.year
        ).count()

        context['new_products'] = current_month_products

        # =========================
        # TOTAL REVENUE
        # =========================

        total_revenue = Order.objects.filter(
            status="Delivered"
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        context['total_revenue'] = total_revenue

        # =========================
        # REVENUE GROWTH
        # =========================

        current_month_revenue = Order.objects.filter(
            status="Delivered",
            created_at__month=current_date.month,
            created_at__year=current_date.year
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        last_month_revenue = Order.objects.filter(
            status="Delivered",
            created_at__month=last_month_date.month,
            created_at__year=last_month_date.year
        ).aggregate(
            total=Sum('total_price')
        )['total'] or 0

        if last_month_revenue > 0:

            revenue_growth = round(
                (
                    (
                        current_month_revenue - last_month_revenue
                    ) / last_month_revenue
                ) * 100
            )

        else:

            revenue_growth = 100 if current_month_revenue > 0 else 0

        context['revenue_growth'] = revenue_growth

        # =========================
        # ORDER STATUS COUNT
        # =========================

        context['pending_count'] = Order.objects.filter(
            status="Pending"
        ).count()

        context['delivered_count'] = Order.objects.filter(
            status="Delivered"
        ).count()

        context['cancelled_count'] = Order.objects.filter(
            status="Cancelled"
        ).count()

        # =========================
        # BEST SELLING PRODUCTS
        # =========================

        best_selling_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).order_by('-total_sold')[:10]

        context['best_selling_products'] = best_selling_products

        # =========================
        # LOW STOCK PRODUCTS
        # =========================

        low_stock_products = Product.objects.filter(
            stock__lte=10
        ).order_by('stock')

        context['low_stock_products'] = low_stock_products

        # =========================
        # PENDING ORDERS
        # =========================

        pending_orders = Order.objects.filter(
            status="Pending"
        ).select_related('user').order_by('-id')[:10]

        context['pending_orders'] = pending_orders

        return context


# ====================================
# Add Product Page View
# ====================================

class AddProductView(TemplateView):

    template_name = "dashboard/add_product.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["colors"] = Color.objects.all()

        context["sizes"] = Size.objects.all()

        return context


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
# Product List View
# ====================================

class ProductlistView(TemplateView):

    template_name = "dashboard/product_list.html"


# ====================================
# Wishlist Dashboard View
# ====================================

class WishlistDashboardView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/wishlist.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        wishlist_data = (
            Wishlist.objects
            .select_related("user", "product")
            .order_by("-id")
        )

        # TOTAL WISHLIST COUNT
        total_wishlist = Wishlist.objects.count()

        # TOTAL USERS USING WISHLIST
        total_users = (
            Wishlist.objects.values("user")
            .distinct()
            .count()
        )

        # MOST WISHLISTED PRODUCTS
        popular_products = (
            Wishlist.objects
            .values("product__name")
            .annotate(total=Count("id"))
            .order_by("-total")[:10]
        )

        context["wishlist_data"] = wishlist_data
        context["total_wishlist"] = total_wishlist
        context["total_users"] = total_users
        context["popular_products"] = popular_products

        return context


# ====================================
# Admin Cart View
# ====================================

class AdminCartView(LoginRequiredMixin, TemplateView):

    template_name = "dashboard/add_to_cart.html"

    def dispatch(self, request, *args, **kwargs):

        # ADMIN ONLY
        if not request.user.is_superuser:
            return redirect("index")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        # CART ITEMS
        cart_data = CartItem.objects.select_related(
            "cart",
            "cart__user",
            "product"
        ).prefetch_related(
            "product__images"
        ).order_by("-id")

        # TOTAL CART ITEMS
        total_cart = cart_data.count()

        # TOTAL USERS
        total_users = cart_data.values(
            "cart__user"
        ).distinct().count()

        # TOTAL AMOUNT
        total_amount = 0

        for item in cart_data:

            total_amount += item.total_price

        context["cart_data"] = cart_data
        context["total_cart"] = total_cart
        context["total_users"] = total_users
        context["total_amount"] = total_amount

        return context


# ====================================
# User List View
# ====================================

class UserListView(ListView):

    model = User

    template_name = "dashboard/user_list.html"

    context_object_name = "users"

    ordering = ['-id']


# ====================================
# USER EDIT PAGE VIEW
# ====================================

class UserEditPageView(TemplateView):

    template_name = "dashboard/user_edit.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        user = get_object_or_404(
            User,
            pk=self.kwargs.get("pk")
        )

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        address = Address.objects.filter(
            user=user
        ).first()

        context["edit_user"] = user

        context["profile"] = profile

        context["address"] = address

        return context


# ====================================
# USER DETAIL API
# ====================================

class UserDetailAPI(View):

    def get(self, request, pk):

        user = get_object_or_404(
            User,
            pk=pk
        )

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        address = Address.objects.filter(
            user=user
        ).first()

        return JsonResponse({

            "id": user.id,

            "first_name": user.first_name,

            "last_name": user.last_name,

            "email": user.email,

            "username": user.username,

            "phone": profile.phone,

            "city": profile.city,

            "bio": profile.bio,

            "address": (
                address.address
                if address
                else ""
            ),

            "state": (
                address.state
                if address
                else ""
            ),

            "pincode": (
                address.pincode
                if address
                else ""
            ),

        })

    def post(self, request, pk):

        user = get_object_or_404(
            User,
            pk=pk
        )

        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.email = request.POST.get("email")
        user.username = request.POST.get("username")

        user.save()

        profile, created = Profile.objects.get_or_create(
            user=user
        )

        profile.phone = request.POST.get("phone")
        profile.city = request.POST.get("city")
        profile.bio = request.POST.get("bio")

        # IMAGE UPDATE

        if request.FILES.get("image"):

            profile.image = request.FILES.get("image")

        profile.save()

        address = Address.objects.filter(
            user=user
        ).first()

        if not address:

            address = Address.objects.create(
                user=user,
                full_name="",
                phone="",
                address="",
                city="",
                state="",
                pincode=""
            )

        address.full_name = request.POST.get("full_name")
        address.phone = request.POST.get("address_phone")
        address.address = request.POST.get("address")
        address.city = request.POST.get("address_city")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")

        address.save()

        return JsonResponse({

            "status": "success"

        })


# ====================================
# USER DELETE VIEW
# ====================================

class UserDeleteView(View):

    def post(self, request, pk):

        user = get_object_or_404(
            User,
            pk=pk
        )

        user.delete()

        return redirect('user_list')


# ====================================
# Admin Order List View
# ====================================

class adminOrderListView(ListView):
    model = Order
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    ordering = ['-id']

    def get_queryset(self):
        return Order.objects.exclude(status__icontains="cancel").order_by('-id')


class OrderListAPI(APIView):

    def get(self, request):

        orders = Order.objects.prefetch_related(
            'items__product__images'
        ).all()

        # --------------------
        # STATUS FILTER
        # --------------------
        status = request.GET.get('status')

        if status:
            orders = orders.filter(status__iexact=status)

        # --------------------
        # DATE FILTER
        # --------------------
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        if start_date:
            orders = orders.filter(created_at__date__gte=parse_date(start_date))

        if end_date:
            orders = orders.filter(created_at__date__lte=parse_date(end_date))

        orders = orders.order_by('-id')

        serializer = OrderSerializer(
            orders,
            many=True,
            context={"request": request}
        )

        return Response(serializer.data)
# ====================================
# Order Detail View
# ====================================
class AdminOrderDetailView(LoginRequiredMixin,DetailView):
    model = Order
    template_name = "dashboard/order_details.html"
    context_object_name = "order"
    pk_url_kwarg = "id"
    login_url = "/"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect("/")
        return super().dispatch(request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        order = self.get_object()
        status = request.POST.get("status")

        if status:

            order.status = status

            order.save()

        return redirect('order_list')

class OrderDetailAPI(APIView):

    def get(self, request, id):

        order = Order.objects.prefetch_related(
            'items__product__images'
        ).get(id=id)

        serializer = OrderSerializer(
            order,
            context={"request": request}
        )

        return Response(serializer.data)
# ====================================
# Order Status Update View
# ====================================

class OrderStatusUpdateView(View):

    def post(self, request, pk):

        order = get_object_or_404(
            Order,
            pk=pk
        )

        new_status = request.POST.get('status')

        if new_status in [
            'pending',
            'accepted',
            'delivered',
            'cancelled'
        ]:

            order.status = new_status

            order.save()

        return redirect('order_list')
    
class OrderStatusUpdateAPI(APIView):

    def patch(self, request, id):
        try:
            order = Order.objects.get(id=id)

            order.status = request.data.get("status")
            order.save()

            return Response({
                "message": "Status updated",
                "status": order.status
            })

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )

class OrderDeleteView(View):

    def post(self, request, id):
        order = get_object_or_404(Order, id=id)
        order.delete()

        messages.success(request, "Order deleted successfully")
        return redirect('order_list')
    
class OrderDeleteAPI(APIView):

    def delete(self, request, id):
        try:
            order = Order.objects.get(id=id)
            order.delete()

            return Response({
                "message": "Order deleted successfully"
            })

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )
class CategoryListAPI(APIView):
    def get(self, request):
        data = Category.objects.all()
        serializer = CategorySerializer(data, many=True)
        return Response(serializer.data)
    
class TypeListAPI(APIView):
    def get(self, request, category_id):
        data = ProductType.objects.filter(category_id=category_id)
        serializer = ProductTypeSerializer(data, many=True)
        return Response(serializer.data)
    
class CategoryCreateAPI(APIView):
    parser_classes = [MultiPartParser, FormParser]  #  MUST

    def post(self, request):
        serializer = CategorySerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success", "message": "Category added"}, status=201)

        return Response({"status": "error", "errors": serializer.errors}, status=400)
    
class ProductTypeCreateAPI(APIView):
    def post(self, request):
        serializer = ProductTypeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Type added"}, status=201)
        return Response(serializer.errors, status=400)
    
class AddColorView(View):

    def post(self, request):

        data = json.loads(request.body)

        color = Color.objects.create(
            name=data.get("name")
        )

        return JsonResponse({
            "id": color.id,
            "name": color.name
        })


# ================= ADD SIZE =================
class AddSizeView(View):

    def post(self, request):

        data = json.loads(request.body)

        size = Size.objects.create(
            name=data.get("name")
        )

        return JsonResponse({
            "id": size.id,
            "name": size.name
        })


# ================= ADD CATEGORY =================
class AddCategoryView(View):

    def post(self, request):

        data = json.loads(request.body)

        category = Category.objects.create(
            name=data.get("name")
        )

        return JsonResponse({
            "id": category.id,
            "name": category.name
        })


# ================= ADD TYPE =================
class AddTypeView(View):

    def post(self, request):

        try:

            data = json.loads(request.body)

            name = data.get("name")

            category_id = data.get("category_id")

            # VALIDATION
            if not name:

                return JsonResponse({
                    "success": False,
                    "message": "Type name required"
                })

            if not category_id:

                return JsonResponse({
                    "success": False,
                    "message": "Category required"
                })

            # CATEGORY
            category = Category.objects.get(
                id=category_id
            )

            # CREATE TYPE
            type_obj = ProductType.objects.create(
                name=name,
                category=category
            )

            return JsonResponse({

                "success": True,

                "id": type_obj.id,

                "name": type_obj.name

            })

        except Exception as e:

            return JsonResponse({

                "success": False,

                "message": str(e)

            }, status=500)
            

class DashboardLoginAPIView(APIView):

    def post(self, request):
        serializer = DashboardLoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data.get("username")
            password = serializer.validated_data.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                if user.is_staff:
                    request.session["dashboard_user_id"] = user.id
                    request.session["dashboard_username"] = user.username
                    request.session["dashboard_email"] = user.email

                    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                    notification_msg = f"User '{user.username}' logged in successfully at {current_time}."
                    
                    AdminNotification.objects.create(
                        user=user,
                        message=notification_msg
                    )

                    return Response({
                        "status": "success",
                        "message": "Dashboard Login Successful"
                    })
                
                return Response({
                    "status": "error",
                    "message": "Access Denied: You are not authorized as an Admin."
                }, status=status.HTTP_403_FORBIDDEN)

            return Response({
                "status": "error",
                "message": "Invalid Username or Password"
            })

        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# =========================
# DASHBOARD LOGOUT API
# =========================

class DashboardLogoutAPIView(APIView):

    def post(self, request):

        # REMOVE ONLY DASHBOARD SESSION

        request.session.pop(
            "dashboard_user_id",
            None
        )

        request.session.pop(
            "dashboard_username",
            None
        )

        request.session.pop(
            "dashboard_email",
            None
        )

        return Response({

            "status": "success",

            "message":
            "Dashboard Logout Successful"

        })
        

class CancelledOrdersTablePage(TemplateView):
    template_name = "dashboard/cancelled_orders.html"
        

class CancelledOrderListAPI(APIView):

    def get(self, request):

        orders = Order.objects.filter(
            status__iexact="Cancelled"
        ).order_by("-id")

        data = []

        for order in orders:

            items = []

            try:
                for item in order.items.all():

                    items.append({
                        "product_name": item.product.name if item.product else "",
                        "quantity": item.quantity
                    })

            except:
                pass

            data.append({
                "id": order.id,
                "user_name": getattr(order.user, "username", "-"),
                "total_price": float(getattr(order, "total_price", 0)),
                "status": order.status,
                "rating": getattr(order, "rating", None),
                "created_at": order.created_at,
                "items": items
            })

        return Response(data)        
        
class CancelledOrderCalendarView(TemplateView):
    template_name = "dashboard/cancelled_order_calendar.html"
    
class OrderCalendarEvents(View):

    def get(self, request, *args, **kwargs):
        orders = (
            Order.objects
            .annotate(hour=TruncHour("created_at"))
            .values("hour")
            .annotate(
                cancelled_count=Count("id", filter=Q(status__iexact="cancelled")),
                other_count=Count("id", filter=~Q(status__iexact="cancelled"))
            )
            .order_by("hour")
        )

        events = []

        for order in orders:
            if order["hour"]:
                time_str = order["hour"].isoformat()
                
                if order["cancelled_count"] > 0:
                    events.append({
                        "title": f"{order['cancelled_count']} Cancelled Orders",
                        "start": time_str,
                        "allDay": False,
                        "color": "#dc3545" # Red
                    })
                
                if order["other_count"] > 0:
                    events.append({
                        "title": f"{order['other_count']} Other Orders",
                        "start": time_str,
                        "allDay": False,
                        "color": "#007bff" # Blue
                    })

        return JsonResponse(events, safe=False)
    

class UserAPI(APIView):
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def get(self, request):
        users = User.objects.all().order_by('-id')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        role = request.data.get('role', 'Customer') 

        # Validation
        if not username or not password:
            return Response({"message": "Username And Password Is Required!"}, status=400)

        if User.objects.filter(username=username).exists():
            return Response({"message": "Username Already Exists!"}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        if role.lower() == 'admin':
            user.is_staff = True      
            user.is_superuser = True 
            user.save()
        else:
            user.is_staff = False    
            user.save()

        Profile.objects.create(
            user=user,
            role=role
        )

        return Response({"message": f"User successfully added as a {role}!"}, status=201)
    
class LoginActivityAPI(APIView):

    def get(self, request):
        logs = LoginActivity.objects.all().order_by('-login_time')
        serializer = LoginActivitySerializer(logs, many=True)
        return Response(serializer.data)
    

class SettingsPageView(TemplateView):
    template_name = "dashboard/settings.html"

    def dispatch(self, request, *args, **kwargs):
        if "dashboard_user_id" not in request.session:
            return redirect("/login-page-url/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.all().order_by('-id')
        context['logs'] = LoginActivity.objects.all().order_by('-login_time')
        
        session_user_id = self.request.session.get("dashboard_user_id")
        if session_user_id:
            context['admin'] = User.objects.filter(id=session_user_id).first()

        return context

    def post(self, request, *args, **kwargs):
        if "dashboard_user_id" in request.session:
            AdminNotification.objects.filter(is_read=False).update(is_read=True)
            return JsonResponse({"status": "success", "message": "Notifications marked as read"})
        return JsonResponse({"status": "error", "message": "Unauthorized"}, status=403)
    
    
class CouponAPI(APIView):

    def get(self, request):
        coupons = Coupon.objects.all().order_by("-id")
        serializer = CouponSerializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CouponSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Coupon added successfully"
            }, status=status.HTTP_201_CREATED)
            
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CouponDetailAPI(APIView):
    def get(self, request, pk):
        try:
            coupon = Coupon.objects.get(id=pk)
            serializer = CouponSerializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({
                "success": False,
                "message": "Coupon not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            coupon = Coupon.objects.get(id=pk)
        except Coupon.DoesNotExist:
            return Response({
                "success": False,
                "message": "Coupon not found"
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CouponSerializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Coupon updated successfully"
            })
            
        return Response({
            "success": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            coupon = Coupon.objects.get(id=pk)
            coupon.delete()
            return Response({
                "success": True,
                "message": "Coupon deleted successfully"
            })
        except Coupon.DoesNotExist:
            return Response({
                "success": False,
                "message": "Coupon not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
class CouponListView(TemplateView):
    template_name = "dashboard/coupon_list.html"
