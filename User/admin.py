from django.contrib import admin
from .models import Product, ProductImage, ProductType, Category, OTP, Profile, Wishlist, Cart, CartItem, Color, Size, Order, OrderItem, Address

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductType)
admin.site.register(Category)
admin.site.register(OTP)
admin.site.register(Profile)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)