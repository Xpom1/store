from django.db import transaction
from django.db.models import F, Sum
from operations.models import Order, OrderProduct, Product, Cart


class OrderCreator:
    def __init__(self, user):
        self.user = user

    @transaction.atomic
    def create_order(self):
        user_balance = self.user.userbalance.balance
        user_cart = self.user.cart
        total_cost = Cart.objects.filter(customer=self.user).aggregate(
            total_sum=Sum(F('products__quantity') * F('product__price'))).get('total_sum')
        if total_cost:
            if user_balance > total_cost:
                self.user.userbalance.remove_balance(total_cost)
                order_id = Order.objects.create(customer=self.user, total_cost=total_cost).id
                order_products = user_cart.products.all()
                for product in order_products:
                    product.order_id = order_id
                    product.price = product.product.price
                OrderProduct.objects.bulk_create(order_products)
                for i in order_products:
                    Product.objects.filter(id=i.product.id).update(quantity=F('quantity') - i.quantity)
                order_products.delete()
                return True, None
            else:
                return False, "Not enough balance"
        else:
            return False, "Cart is empty"
