from django.contrib import admin
from django.urls import path

from .views import *
urlpatterns = [
    path('cart/', CartView.as_view(), name='cart'),

path(
    'cart/add/<int:product_id>/',
    AddToCartView.as_view(),
    name='add_to_cart'
),

path(
    'cart/update/<int:pk>/',
    UpdateCartView.as_view(),
    name='update_cart'
),

path(
    'cart/remove/<int:cart_id>/',
    RemoveCartView.as_view(),
    name='remove_cart'
),
]