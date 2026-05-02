from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

class ProductType(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="types")

    def __str__(self):
        return self.name

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
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')

# models.py
from django.db import models
from django.utils import timezone

class OTP(models.Model):
    email = models.CharField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 300  # 5 min