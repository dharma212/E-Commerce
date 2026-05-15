from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# ====================================
# Category
# ====================================
class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

# ====================================
# Product Type
# ====================================
class ProductType(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="types")

    def __str__(self):
        return self.name

# ====================================
# Product
# ====================================
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    price = models.IntegerField()   
    discount = models.IntegerField(default=0)   
    stock = models.IntegerField()
    description = models.TextField(default=0)
    mrp = models.IntegerField(default=0)

    def final_price(self):
        if self.mrp > 0:
            return self.mrp - self.discount
        return self.price   

    def discount_percent(self):
        if self.mrp > 0:
            return round((self.discount / self.mrp) * 100)
        return 0
   
# ==================================== 
# Product Image 
# ==================================== 
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

# ====================================
# OTP
# ====================================
class OTP(models.Model):
    username = models.CharField(max_length=50)
    email = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300  
    
    def __str__(self):
        return self.username
    
# ====================================
# Profile
# ====================================
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="profile/", blank=True, null=True)
    
    def __str__(self):
        return self.phone
    
# ====================================
# Wishlist
# ====================================
class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
    
# ====================================
# Cart
# ====================================
class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# ====================================
# Cart Item
# ====================================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey('Product',on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.product.final_price() * self.quantity

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"