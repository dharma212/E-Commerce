from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path(
        'checkout/',
        checkoutview.as_view(),
        name='checkout'
    ),

    path(
        'my-orders/',
        OrderListView.as_view(),
        name='my_orders'
    ),

    path(
        'order/<int:pk>/',
        OrderDetailView.as_view(),
        name='order_details'
    ),
    
]