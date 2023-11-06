from django.test import TestCase
from django.contrib.auth.models import User
from operations.models import Сategory, Product, Cart, CartProduct, Rating_Feedback, ProductPriceInfo


class ShopTests(TestCase):
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

    def test_category_str(self):
        self.assertEqual(str(self.category), 'Electronics')

    def test_product_discount_calculation(self):
        self.assertEqual(self.product.discount, 17)

    def test_product_save_price_logic(self):
        with self.assertRaises(ValueError):
            self.product.price = 130.0
            self.product.save()

    def test_cart_str(self):
        cart = Cart.objects.create(customer=self.user)
        self.assertEqual(str(cart), 'Cart - testuser')

    def test_cart_product_str(self):
        cart = Cart.objects.create(customer=self.user)
        cart_product = CartProduct.objects.create(cart=cart, product=self.product)
        self.assertEqual(str(cart_product), 'testuser - Camera - 100.0руб - 1')

    def test_rating_feedback_constraints(self):
        with self.assertRaises(ValueError):
            Rating_Feedback.objects.create(user=self.user, product=self.product, feedback='Great!').save()

        parent_feedback = Rating_Feedback.objects.create(user=self.user, product=self.product, rating=5,
                                                         feedback='Great!')
        with self.assertRaises(ValueError):
            Rating_Feedback.objects.create(user=self.user, parent=parent_feedback, rating=5).save()

        with self.assertRaises(ValueError):
            Rating_Feedback.objects.create(user=self.user, parent=parent_feedback).save()

    def test_product_price_info_str(self):
        product_price_info = ProductPriceInfo.objects.create(product=self.product, price=95.0)
        self.assertEqual(str(product_price_info), 'Camera - 95.0')

