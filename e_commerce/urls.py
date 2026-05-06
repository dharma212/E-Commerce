from django.contrib import admin
from django.urls import path
from User.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',IndexView.as_view(),name="index"),
    path('shop/',shopview.as_view(),name="shop"),
    path('detail/',detailview.as_view(),name="detail"),
    path('contact/',contactview.as_view(),name="contact"),
    path('cart/',cartview.as_view(),name="cart"),
    path('checkout/',checkoutview.as_view(),name="checkout"),
    
    path('dashboard/index/',Dashboardview.as_view(),name="dashboard"),
    path('api/categories/', CategoryListAPI.as_view()),
    path('api/types/<int:category_id>/', TypeListAPI.as_view()),
    path('api/add-product/', ProductCreateAPI.as_view(), name='add_product'),
    path('add-product-page/', AddProductPageView.as_view(), name='add_product'),
    
    path('add-category/', AddCategoryPageView.as_view(), name='add_category'),
    path('add-type/', AddTypePageView.as_view(), name='add_type'),

    path('api/add-category/', CategoryCreateAPI.as_view()),
    path('api/add-type/', ProductTypeCreateAPI.as_view()),
    path('api/categories/', CategoryListAPI.as_view()),
    path('api/products/', ProductListAPI.as_view(), name='api_products'),
    path('products/list/', ProductlistView.as_view(), name='product_list'),

    path('auth/',AuthPageView.as_view(),name='auth'),
    path('api/send-otp/', SendOTPView.as_view(), name="send_otp"),
    path('api/verify-otp/', VerifyOTPView.as_view(), name="verify_otp"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api/user-profile/', ProfileAPI.as_view(), name='user_profile'),
    path('profile/', ProfilePageView.as_view(), name='profile'),
    path("api/upload-image/", UploadImageView.as_view()),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
