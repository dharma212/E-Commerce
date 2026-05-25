# models.py

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# ====================================
# CATEGORY
# ====================================

class Category(models.Model):

    name = models.CharField(max_length=100)

    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


# ====================================
# PRODUCT TYPE
# ====================================

class ProductType(models.Model):

    name = models.CharField(max_length=100)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="types"
    )

    def __str__(self):
        return self.name


# ====================================
# COLOR
# ====================================

class Color(models.Model):

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


# ====================================
# SIZE
# ====================================

class Size(models.Model):

    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name


# ====================================
# PRODUCT
# ====================================

class Product(models.Model):

    name = models.CharField(max_length=200)

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )

    type = models.ForeignKey(
        ProductType,
        on_delete=models.CASCADE
    )

    price = models.IntegerField()

    discount = models.IntegerField(default=0)

    stock = models.IntegerField()

    description = models.TextField(default=0)

    mrp = models.IntegerField(default=0)

    color = models.ForeignKey(
        Color,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def final_price(self):

        if self.mrp > 0:
            return self.mrp - self.discount

        return self.price

    def discount_percent(self):

        if self.mrp > 0:
            return round((self.discount / self.mrp) * 100)

        return 0

    def __str__(self):
        return self.name


# ====================================
# PRODUCT IMAGE
# ====================================

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.product.name


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
# PROFILE
# ====================================

class Profile(models.Model):

    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Customer', 'Customer'),
        ('Seller', 'Seller'),
    )

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Customer'
    )

    phone = models.CharField(max_length=10, blank=True)

    city = models.CharField(max_length=100, blank=True)

    bio = models.TextField(blank=True)

    image = models.ImageField(
        upload_to="profile/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# ====================================
# WISHLIST
# ====================================

class Wishlist(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


# ====================================
# CART
# ====================================

class Cart(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


# ====================================
# CART ITEM
# ====================================

class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):

        return self.product.final_price() * self.quantity

    def __str__(self):

        return f"{self.product.name} - {self.quantity}"


# ====================================
# ADDRESS
# ====================================

class Address(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(max_length=150)

    phone = models.CharField(max_length=10)

    address = models.TextField()

    city = models.CharField(max_length=100)

    state = models.CharField(max_length=100)

    pincode = models.CharField(max_length=6)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        if self.is_default:

            Address.objects.filter(
                user=self.user
            ).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):

        return self.full_name


# ====================================
# ORDER
# ====================================

class Order(models.Model):

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):

        return f"Order #{self.id}"


# ====================================
# ORDER ITEM
# ====================================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        related_name='items',
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):

        return self.product.name