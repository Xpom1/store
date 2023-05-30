from django.db import models
from django.contrib.auth.models import User


class Cart(models.Model):
    customer_id = models.ForeignKey(User, on_delete=models.PROTECT)
    product_id = models.ManyToManyField('Product')

    def __str__(self):
        return f'Cart - {User.get_username(self.customer_id)}'



class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)
    price = models.IntegerField()

    def __str__(self):
        return f'{self.name} - {self.price}руб'


class Product_photo(models.Model):
    url = models.URLField(max_length=200)
    product_id = models.ForeignKey('Product', on_delete=models.PROTECT)


