from django.test import TestCase
from django.contrib.auth.models import User
from operations.serializers import (
    RatingFeedbackSerializer,
    ProductRetrieveSerializer,
    CartProductSerializer,
)
from operations.models import Product, Сategory, Cart, CartProduct, Rating_Feedback, ProductPriceInfo


class SerializerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Сategory.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Camera',
            description='A great camera.',
            price=100.0,
            quantity=10,
            old_price=120.0
        )
        self.product.category.add(self.category)

        self.rating_feedback = Rating_Feedback.objects.create(
            user=self.user,
            product=self.product,
            rating=5,
            feedback='Great product!'
        )

    def test_rating_feedback_serializer(self):
        serializer = RatingFeedbackSerializer(instance=self.rating_feedback)
        data = serializer.data
        self.assertEqual(data['user'], self.user.id)
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['feedback'], 'Great product!')

    def test_product_retrieve_serializer(self):
        ProductPriceInfo.objects.create(product=self.product, price=95.0)
        ProductPriceInfo.objects.create(product=self.product, price=90.0)

        serializer = ProductRetrieveSerializer(instance=self.product)
        data = serializer.data
        val = ['id', 'name', 'description', 'price', 'available', 'quantity',
               'category', 'old_price', 'discount', 'attributes', 'rating_feedback',
               'product_price_history']
        self.assertEqual(set(data.keys()), set(val))
        self.assertEqual(len(data['product_price_history']), 2)

    def test_cart_product_serializer(self):
        cart = Cart.objects.create(customer=self.user)
        cart_product = CartProduct.objects.create(cart=cart, product=self.product, quantity=2)
        serializer = CartProductSerializer(instance=cart_product)
        data = serializer.data
        self.assertEqual(data['product_id'], self.product.id)
        self.assertEqual(data['product_name'], 'Camera')
        self.assertEqual(data['product_price'], 100.0)
        self.assertEqual(data['quantity'], 2)
