from rest_framework import serializers
from .models import Product, Cart, CartProduct, Order, OrderProduct, Rating_Feedback, ProductPriceInfo


class CommentSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        self.fields['feedback_comment'] = CommentSerializer(many=True, read_only=True)
        return super(CommentSerializer, self).to_representation(instance)

    class Meta:
        model = Rating_Feedback
        fields = ('user_id', 'feedback', 'id', 'commented_id', 'feedback_comment', )


class ProductRetrieveSerializer(serializers.ModelSerializer):
    class ProductPriceHistory(serializers.ModelSerializer):
        class Meta:
            model = ProductPriceInfo
            fields = ('price', 'timestamp', )

    class RatingFeedbackSerializer(serializers.ModelSerializer):
        feedback_comment = CommentSerializer(many=True, read_only=True)

        class Meta:
            model = Rating_Feedback
            fields = ('user', 'rating', 'feedback', 'id', 'feedback_comment',)

    attributes = serializers.DictField(source='eav.get_values_dict', read_only=True)
    rating_feedback = RatingFeedbackSerializer(source='rating_feedback_set', many=True, read_only=True)
    product_price_history = ProductPriceHistory(many=True, read_only=True, source='productpriceinfo_set')

    class Meta:
        model = Product
        fields = '__all__'


class ProductListSerializers(serializers.ModelSerializer):
    rating = serializers.FloatField()
    count = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'price', 'rating', 'count')


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
