from rest_framework import serializers
from .models import Product, Cart, CartProduct
from django.contrib.auth.models import User


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductListViewCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


class CartProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartProduct
        fields = '__all__'


class ProductCartSerializer(serializers.ModelSerializer):
    cart_product = CartProductSerializer(source='cartproduct_set')

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'cart_product',)


class CartSerializer(serializers.ModelSerializer):
    product = ProductCartSerializer(many=True)

    class Meta:
        model = Cart
        fields = ('id', 'product',)
