from rest_framework import serializers
from .models import Cart, CartItem
from productos.serializers import ProductoSerializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductoSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'price']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'subtotal', 'iva', 'total', 'created_at', 'updated_at']
