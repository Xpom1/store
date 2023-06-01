from rest_framework import serializers
from .models import Product, Cart
from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    customer = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Cart
        fields = ('id', 'customer', 'product')
