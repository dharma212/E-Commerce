from django.db.models import Avg
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.utils.text import slugify

# ====================================
# CATEGORY
# ====================================
class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    image = models.ImageField(upload_to='categories/',null=True,blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

# ====================================
# PRODUCT TYPE
# ====================================
class ProductType(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="types")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
    slug = models.SlugField(blank=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    type = models.ForeignKey(ProductType,on_delete=models.CASCADE)
    discount = models.IntegerField(default=0)
    stock = models.IntegerField()
    description = models.TextField(default=0)
    mrp = models.IntegerField(default=0)
    colors = models.ManyToManyField(Color)
    sizes = models.ManyToManyField(Size)
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1

            while Product.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)
    
    def average_rating(self):

        avg = Review.objects.filter(
            order__items__product=self
        ).aggregate(
            Avg('rating')
        )['rating__avg']

        return round(avg or 0, 1)

    def total_reviews(self):

        return Review.objects.filter(
            order__items__product=self
        ).count()

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
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/')
    color = models.ForeignKey(
        Color,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    size = models.ForeignKey(
        Size,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

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
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=20,choices=ROLE_CHOICES,default='Customer')
    phone = models.CharField(max_length=10, blank=True)
    city = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="profile/",blank=True,null=True)

    def __str__(self):
        return self.user.username

# ====================================
# WISHLIST
# ====================================
class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

# ====================================
# CART
# ====================================
class Cart(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

# ====================================
# CART ITEM
# ====================================
class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    color = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=""
    )

    size = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=""
    )

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
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="addresses")
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
            Address.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name

# ====================================
# ORDER
# ====================================
class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Packed', 'Packed'),
        ('Shipped', 'Shipped'),
        ('Out For Delivery', 'Out For Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True,blank=True)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50) 
    cancel_reason = models.TextField(
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Order #{self.id}"

# ====================================
# ORDER ITEM
# ====================================
class OrderItem(models.Model):
    order = models.ForeignKey(Order,related_name='items',on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    color = models.CharField(max_length=50,blank=True,null=True)
    size = models.CharField(max_length=50,blank=True,null=True)

    def __str__(self):
        return self.product.name    
    
class Review(models.Model):
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    rating = models.PositiveSmallIntegerField()

    description = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)