from rest_framework.response import Response
from django.db.models import F
from django.db.models.functions import Least

from operations.models import Product
from operations.serializers import CartSerializer


class CartOperation:

    def __init__(self, user, queryset):
        self.user = user
        self.queryset = queryset

    def list_cart(self):
        queryset = self.queryset
        serializer = CartSerializer(queryset, many=True)
        cart = queryset.first()
        if cart:
            cart.products.filter(product__quantity=0).delete()
            products_to_update = cart.products.all().select_related('product')
            for product in products_to_update:
                product.quantity = min(product.product.quantity, product.quantity)
            cart.products.bulk_update(products_to_update, ['quantity'])
        return Response(serializer.data)

    def change_product_quantity(self, product_id, command):
        try:
            product_quantity = int(self.queryset[0].product.filter(id=product_id).values()[0].get('quantity'))
            cart_product = self.queryset[0].products.filter(product_id=product_id)
            if command.isdigit():
                cart_product.update(quantity=Least(product_quantity, int(command)))
                return True, cart_product
            elif command == 'add':
                cart_product.update(quantity=Least(product_quantity, F('quantity') + 1))
                return True, cart_product
            elif command == 'reduce':
                if cart_product[0].quantity > 1:
                    cart_product.update(quantity=Least(product_quantity, F('quantity') - 1))
                    return True, cart_product
                else:
                    cart_product.delete()
                    return False, None
            else:
                return None, None
        except IndexError:
            return None, None

    def add_product(self, product_id, quantity):
        try:
            product = Product.objects.get(id=product_id)
            if 0 < quantity <= product.quantity:
                self.queryset.first().products.create()
                return True
            else:
                return False
        except Product.DoesNotExist:
            return False

    def remove_product(self, product_id):
        deleted, _ = self.cart.products.filter(product_id=product_id).delete()
        return deleted > 0



