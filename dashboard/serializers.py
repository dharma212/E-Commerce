# dashboard/serializers.py

from rest_framework import serializers
from User.models import *

class DashboardLoginSerializer(serializers.Serializer):

    username = serializers.CharField()

    password = serializers.CharField()
    

class OrderItemSerializer(serializers.ModelSerializer):

    product_name = serializers.CharField(
        source='product.name'
    )

    product_image = serializers.SerializerMethodField()

    class Meta:

        model = OrderItem

        fields = [
            'id',
            'product_name',
            'product_image',
            'quantity',
        ]

    def get_product_image(self, obj):

        image = obj.product.images.first()

        if image and image.image:

            request = self.context.get("request")

            if request:
                return request.build_absolute_uri(
                    image.image.url
                )

            return image.image.url

        return None


class OrderSerializer(serializers.ModelSerializer):

    user_name = serializers.CharField(
        source='user.username'
    )

    address = serializers.CharField(
        source='address.address',
        default=''
    )

    items = serializers.SerializerMethodField()

    class Meta:

        model = Order

        fields = [
            'id',
            'user_name',
            'address',
            'total_price',
            'status',
            'created_at',
            'items'
        ]

    def get_items(self, obj):

        serializer = OrderItemSerializer(
            obj.items.all(),
            many=True,
            context=self.context
        )

        return serializer.data