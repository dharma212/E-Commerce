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
    path(
    'invoice/<int:pk>/',
    InvoiceView.as_view(),
    name='invoice'
),

path(
    'add-review/<int:pk>/',
    AddReviewView.as_view(),
    name='add_review'
),
path(
    "order/<int:pk>/cancel/",
    CancelOrderView.as_view(),
    name="cancel_order"
),

path(
    "order/<int:pk>/reorder/",
    ReOrderView.as_view(),
    name="reorder_order"
),
path(
    "apply-coupon/",
    ApplyCouponView.as_view(),
    name="apply_coupon"
),
path('dismiss-coupon/', DismissCouponView.as_view(), name='dismiss_coupon'),   
]