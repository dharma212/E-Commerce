from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    type_name = serializers.CharField(
        source='type.name',
        read_only=True
    )

    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    colors = serializers.PrimaryKeyRelatedField(
        queryset=Color.objects.all(),
        many=True
    )

    sizes = serializers.PrimaryKeyRelatedField(
        queryset=Size.objects.all(),
        many=True
    )

    class Meta:

        model = Product

        fields = '__all__'

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):

    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'role'
        ]

    def get_role(self, obj):
        try:
            return obj.profile.role
        except:
            return "Customer"
        

class LoginActivitySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = LoginActivity
        fields = ['user', 'login_time', 'logout_time', 'ip_address']