from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # =========================
    # ADMIN
    # =========================
    path('admin/', admin.site.urls),

    # =========================
    # APPS URLS
    # =========================
    path('', include('dashboard.urls')),
    path('', include('product.urls')),
    path('', include('order.urls')),
    path('', include('cart.urls')),
    path('', include('wishlist.urls')),
    path('', include('User.urls')),

]

# =========================
# MEDIA FILES
# =========================
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )