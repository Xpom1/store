from rest_framework import serializers
from .models import Product, Cart, CartProduct


class ProductListSerializer(serializers.ModelSerializer):
    # 'dict' object has no attribute 'validate_attributes' это происходит из-за того, что он не может проверить
    # валидность attributes
    # partial_update, но тоже не работает
    # attributes = serializers.DictField(source='eav.get_values_dict')

    class Meta:
        model = Product
        fields = '__all__'


class ProductListViewCart(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


class CartProductSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source='product.id')
    product_name = serializers.CharField(source='product.name')
    product_price = serializers.FloatField(source='product.price')

    class Meta:
        model = CartProduct
        fields = ('product_id', 'product_name', 'product_price', 'quantity',)


class CartSerializer(serializers.ModelSerializer):
    products = CartProductSerializer(many=True)
    total_sum = serializers.FloatField()

    class Meta:
        model = Cart
        fields = ('id', 'products', 'total_sum',)
