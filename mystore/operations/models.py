from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q
from eav.decorators import register_eav
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel


class Сategory(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.name}'


@register_eav()
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1024, null=True)
    price = models.FloatField()
    available = models.BooleanField(default=True)
    quantity = models.IntegerField(default=0)
    category = models.ManyToManyField(Сategory, related_name='products')
    old_price = models.FloatField()
    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def save(self, *args, **kwargs):
        self.old_price = self.old_price or self.price
        if self.old_price < self.price:
            raise ValueError("Old price must be greater than or equal to price")
        self.discount = round(1 - self.price / self.old_price, 2) * 100
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.price}руб'


class Cart(models.Model):
    customer = models.OneToOneField(User, on_delete=models.PROTECT)
    product = models.ManyToManyField(Product, through='CartProduct')

    def name_owner_cart(self):
        return f'{User.get_username(self.customer)}'

    def __str__(self):
        return f'Cart - {User.get_username(self.customer)}'


class ProductPhoto(models.Model):
    url = models.URLField()
    product = models.ForeignKey('Product', on_delete=models.PROTECT)


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, related_name='products', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{Cart.name_owner_cart(self.cart)} - {self.product} - {self.quantity}'


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ManyToManyField(Product, through='OrderProduct')
    timestamp = models.DateTimeField(auto_now_add=True)
    total_cost = models.PositiveIntegerField()


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.PositiveIntegerField()


class Rating_Feedback(MPTTModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    rating = models.PositiveIntegerField(null=True)
    feedback = models.CharField(max_length=255, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def save(self, *args, **kwargs):
        if self.parent is None:
            if self.rating is None:
                raise ValueError("When adding feedback, you must specify the rating")
            super(Rating_Feedback, self).save(*args, **kwargs)
        else:
            if self.rating is not None:
                raise ValueError("You can't leave the rating on someone else's rating")
            elif self.feedback is None:
                raise ValueError("You can't leave comments without text")
            self.product = None
            super(Rating_Feedback, self).save(*args, **kwargs)

    class Meta:
        constraints = [models.UniqueConstraint(condition=Q(parent=None), fields=['user', 'product'],
                                               name='Checking the existence of a parent')]

    def __str__(self):
        return f'{self.user} - {self.feedback}'


class ProductPriceInfo(models.Model):
    price = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.product.name} - {self.price}'
