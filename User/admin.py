from django.contrib import admin
from .models import Product, ProductImage, ProductType, Category

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductType)
admin.site.register(Category)