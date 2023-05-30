from django.db import models
from django.contrib.auth.models import User


class Cart(models.Model):
    customer = models.ForeignKey(User, on_delete=models.PROTECT)
    product = models.ManyToManyField('Product')

    def __str__(self):
        return f'Cart - {User.get_username(self.customer)}'


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)
    price = models.FloatField()

    def __str__(self):
        return f'{self.name} - {self.price}руб'


class ProductPhoto(models.Model):
    url = models.URLField()
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
