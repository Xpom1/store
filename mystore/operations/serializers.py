from rest_framework import serializers
from .models import Product, Cart, CartProduct, Order, OrderProduct


class ProductRetrieveSerializer(serializers.ModelSerializer):
    attributes = serializers.DictField(source='eav.get_values_dict', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializers(serializers.ModelSerializer):
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


class OrderSerializer(serializers.ModelSerializer):
    class OrderProductListSerializer(serializers.ModelSerializer):
        product_name = serializers.CharField(source='product.name')

        class Meta:
            model = OrderProduct
            fields = ('product_name', 'quantity', 'price',)

    product = OrderProductListSerializer(many=True, source='orderproduct_set')

    class Meta:
        model = Order
        fields = '__all__'
