from rest_framework import serializers
from .models import Product, Cart_Product
from django.contrib.auth.models import User


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductListViewCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'category')


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart_Product
        fields = ('product', 'quantity')
