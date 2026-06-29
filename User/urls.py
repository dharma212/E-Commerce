from django.contrib import admin
from django.urls import path

from .views import *
urlpatterns = [
    # ====================================
# URLS
# ====================================

path('', IndexView.as_view(), name='index'),

path('contact/', contactview.as_view(), name='contact'),

# ====================================
# AUTHENTICATION
# ====================================

path('auth/', LoginPageView.as_view(), name='auth'),

path('logout/', LogoutView.as_view(), name='logout'),

# ====================================
# OTP API
# ====================================

path(
    'api/send-otp/',
    SendOTPView.as_view(),
    name='send_otp'
),

path(
    'api/verify-otp/',
    VerifyOTPView.as_view(),
    name='verify_otp'
),

# ====================================
# PROFILE
# ====================================

path(
    'user-profile/',
    ProfileView.as_view(),
    name='profile'
),

path(
    'api/user-profile/',
    ProfileAPI.as_view(),
    name='profile_api'
),

path(
    'api/upload-image/',
    UploadImageView.as_view(),
    name='upload_image'
),

# ====================================
# ADDRESS
# ====================================

path(
    'address/add/',
    AddAddressView.as_view(),
    name='add_address'
),

path(
    'address/delete/<int:id>/',
    DeleteAddressView.as_view(),
    name='delete_address'
),

path(
    'set-default-address/<int:id>/',
    SetDefaultAddressView.as_view(),
    name='set_default_address'
),
path('signup/', SignupPageView.as_view(), name='signup'),
]