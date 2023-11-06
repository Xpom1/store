from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from operations.models import Product, Cart, Order, Rating_Feedback, Сategory, CartProduct
from operations.serializers import ProductRetrieveSerializer, CartSerializer, OrderSerializer


class ProductViewSetTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Сategory.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Camera', description='A great camera.', price=100.0, quantity=10)
        self.product.category.add(self.category)
        self.client.login(username='testuser', password='testpassword')

    def test_list_products(self):
        url = reverse('products-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CartViewSetTestCase(APITestCase):

    def setUp(self):
        # Create a user, a product and a cart for the test case
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.category = Сategory.objects.create(name='Electronics')
        self.product = Product.objects.create(
            name='Camera', description='A great camera.', price=100.0, quantity=10)
        self.product.category.add(self.category)
        self.cart = Cart.objects.create(customer=self.user)
        self.cart_product = CartProduct.objects.create(cart=self.cart, product=self.product, quantity=1)

        # Log in the user
        self.client.login(username='testuser', password='testpassword')

    def test_list_cart(self):
        url = reverse('cart-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
