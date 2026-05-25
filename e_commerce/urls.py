from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from User.views import *

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # WEBSITE PAGES
    # =========================
    path('', IndexView.as_view(), name='index'),
    path('shop/', ShopView.as_view(), name='shop'),
    path('contact/', contactview.as_view(), name='contact'),
    path('checkout/', checkoutview.as_view(), name='checkout'),

    # =========================
    # PRODUCT
    # =========================
    path('product/<int:id>/', ProductDetailView.as_view(), name='product_detail'),
    path('search-product/', SearchProductView.as_view(), name='search_product'),
    path('products/list/', ProductlistView.as_view(), name='product_list'),

    # =========================
    # AUTHENTICATION
    # =========================
    path('auth/', LoginPageView.as_view(), name='auth'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # =========================
    # OTP API
    # =========================
    path('api/send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('api/verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),

    # =========================
    # PROFILE
    # =========================
    path('user-profile/', ProfileView.as_view(), name='profile'),
    path('api/user-profile/', ProfileAPI.as_view(), name='profile_api'),
    path('api/upload-image/', UploadImageView.as_view(), name='upload_image'),

    # =========================
    # ADDRESS
    # =========================
    path('address/add/', AddAddressView.as_view(), name='add_address'),
    path('address/delete/<int:id>/', DeleteAddressView.as_view(), name='delete_address'),

    # =========================
    # WISHLIST
    # =========================
    path('wishlist/', WishlistPageView.as_view(), name='wishlist'),
    path('api/wishlist/', WishlistAPIView.as_view(), name='wishlist_api'),
    path('api/wishlist/data/', WishlistDataAPIView.as_view(), name='wishlist_data'),

    # =========================
    # CART
    # =========================
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/update/<int:pk>/', UpdateCartView.as_view(), name='update_cart'),
    path('cart/remove/<int:cart_id>/', RemoveCartView.as_view(), name='remove_cart'),

    # =========================
    # ORDERS
    # =========================
    path('my-orders/', OrderListView.as_view(), name='my_orders'),

    # =========================
    # DASHBOARD
    # =========================
    path('dashboard/', Dashboardview.as_view(), name='dashboard'),

    # =========================
    # PRODUCT MANAGEMENT
    # =========================
    path('dashboard/add-product/', AddProductView.as_view(), name='add_product_page'),
    path('api/add-product/', ProductCreateAPI.as_view(), name='add_product'),

    # =========================
    # CATEGORY
    # =========================
    path('dashboard/add-category/', AddCategoryPageView.as_view(), name='add_category_page'),
    path('api/add-category/', AddCategoryView.as_view(), name='add_category'),

    # =========================
    # PRODUCT TYPE
    # =========================
    path('dashboard/add-type/', AddTypePageView.as_view(), name='add_type_page'),
    path('api/add-type/', AddTypeView.as_view(), name='add_type'),

    # =========================
    # COLOR & SIZE
    # =========================
    path('api/add-color/', AddColorView.as_view(), name='add_color'),
    path('api/add-size/', AddSizeView.as_view(), name='add_size'),

    # =========================
    # API DATA
    # =========================
    path('api/categories/', CategoryListAPI.as_view(), name='categories'),
    path('api/types/<int:category_id>/', TypeListAPI.as_view(), name='types'),
    path('api/products/', ProductListAPI.as_view(), name='api_products'),
    path(
        'set-default-address/<int:id>/',
        SetDefaultAddressView.as_view(),
        name='set_default_address'
    ),
    path(
        "dashboard/wishlist/",
        WishlistDashboardView.as_view(),
        name="dashboard_wishlist"
    ),
    path(
        "dashboard/cart/",
        AdminCartView.as_view(),
        name="admin_cart"
    ),
    path(
        "order/<int:pk>/",
        OrderDetailView.as_view(),
        name="order_details"
    ),
      path(
        'users/',
        UserListView.as_view(),
        name='user_list'
    ),
      path(
        'orders/',
        adminOrderListView.as_view(),
        name='order_list'
    ),
]

# =========================
# MEDIA FILES
# =========================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )