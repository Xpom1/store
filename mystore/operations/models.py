from django.db import models
from django.contrib.auth.models import User


class Сategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)
    price = models.FloatField()
    available = models.BooleanField(default=True)
    quantity = models.IntegerField()
    category = models.ManyToManyField(Сategory, related_name='products')

    def __str__(self):
        return f'{self.name} - {self.price}руб'


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ManyToManyField(Product, through='CartProduct')

    def name_owner_cart(self):
        return f'{User.get_username(self.customer)}'

    def __str__(self):
        return f'Cart - {User.get_username(self.customer)}'


class ProductPhoto(models.Model):
    url = models.URLField()
    product = models.ForeignKey('Product', on_delete=models.PROTECT)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{Cart.name_owner_cart(self.cart)} - {self.product}'



# Нужно ли нам отзеркаливать поведения CartProduct? - Нужно, тк ты никак не сможешь узнать сколько конкретно у тебя в
# заказе количества товаров

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through='OrderProduct')
    timestamp = models.DateTimeField(auto_now_add=True)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
