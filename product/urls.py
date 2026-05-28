from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # PRODUCT
    # =========================
    path(
        'shop/',
        ShopView.as_view(),
        name='shop'
    ),

    path(
        'product/<int:id>/',
        ProductDetailView.as_view(),
        name='product_detail'
    ),

    path(
        'search-product/',
        SearchProductView.as_view(),
        name='search_product'
    ),

    # =========================
    # PRODUCT API
    # =========================
    path(
        'api/products/',
        ProductListAPI.as_view(),
        name='api_products'
    ),

    path(
        'api/add-product/',
        ProductCreateAPI.as_view(),
        name='add_product'
    ),
     path(
        'api/products/<int:pk>/delete/',
        ProductDeleteAPI.as_view()
    ),

    path(
        'api/products/<int:pk>/update/',
        ProductUpdateAPI.as_view()
    ),
    path('buy-now-api/', BuyNowAPI.as_view(), name='buy_now_api'),
]

# =========================
# MEDIA FILES
# =========================
if settings.DEBUG:

    urlpatterns += static(

        settings.MEDIA_URL,

        document_root=settings.MEDIA_ROOT

    )