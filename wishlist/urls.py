from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    # =========================================
# URLS
# =========================================

path(
    'wishlist/',
    WishlistPageView.as_view(),
    name='wishlist'
),

path(
    'api/wishlist/',
    WishlistAPIView.as_view(),
    name='wishlist_api'
),

path(
    'api/wishlist/data/',
    WishlistDataAPIView.as_view(),
    name='wishlist_data'
),
]