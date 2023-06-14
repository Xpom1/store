from django.db.models import Sum, F
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import mixins, filters
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Cart, CartProduct
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductListSerializer, CartSerializer, ProductListViewCart, CartProductSerializer


class ProductViewSet(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        return Product.objects.filter(id=self.kwargs['pk'])


class ProductViewSmallerVersion(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListViewCart
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'price']
    permission_classes = (IsAdminOrReadOnly,)


class ManyCartAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Cart.objects.all().annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        )


class Handler():

    def success_with_data(self, data):
        return Response({"status": "success", "data": data.values()})

    def success(self):
        return Response({"status": "success"})

    def max_quantity(self, quantity):
        return Response({'error': f'Max quantity of this product {quantity}'})

    def deleted(self):
        return Response({'Deleted': 'Deleted'})

    def indexerror(self):
        return Response({'error': f'Такого товара нет в корзине.'})

    def unrecognized_command(self):
        return Response({'error': 'Unknown command. To change it, '
                                  'you need to use "add" or "reduce" '
                                  'or enter a number of times.'})


class CartAPIView(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)

    @action(methods=['put'], detail=False)
    def change(self, request):
        data = request.data
        product_id = data.get('product_id')
        command = data.get('command').strip()

        try:
            product_quantity = int(self.get_queryset()[0].product.filter(id=product_id).values()[0].get('quantity'))
            concrete_product = self.get_queryset()[0].products.filter(product_id=product_id)
            if command.isdigit():
                command = int(command)
                if command <= product_quantity:
                    concrete_product.update(quantity=command)
                    return Handler().success_with_data(data=concrete_product)
                return Handler().max_quantity(quantity=product_quantity)
            elif command == 'add':
                cart_produkt_id = concrete_product.values()[0].get('quantity')
                if cart_produkt_id + 1 <= product_quantity:
                    concrete_product.update(quantity=cart_produkt_id + 1)
                    return Handler().success_with_data(data=concrete_product)
                return Handler().max_quantity(quantity=product_quantity)
            elif command == 'reduce':
                cart_produkt_id = concrete_product.values()[0].get('quantity')
                if cart_produkt_id - 1 > 0:
                    concrete_product.update(quantity=cart_produkt_id - 1)
                    return Handler().success_with_data(data=concrete_product)
                if cart_produkt_id == 1:
                    concrete_product.delete()
                    return Handler().deleted()
            else:
                return Handler().unrecognized_command()
        except IndexError:
            return Handler().indexerror()

    # Почему удаляет даже неизвестный ID
    @action(methods=['delete'], detail=False)
    def delete(self, request):
        data = request.data
        try:
            product_id = data.get('product_id')
            self.get_queryset()[0].products.filter(product_id=product_id).delete()
            return Handler().success()
        except IndexError:
            return Handler().indexerror()

    @action(methods=['post'], detail=False)
    def add(self, request):
        data = request.data
        try:
            product_id = data.get('product_id')
            cart_id = self.get_queryset()[0].id
            product_quantity = int(Product.objects.filter(id=product_id).values()[0].get('quantity'))
            quantity = int(data.get('quantity'))
            if 0 < quantity <= product_quantity:
                self.get_queryset()[0].products.create(quantity=quantity, cart_id=cart_id, product_id=product_id)
                return Handler().success()
            return Handler().max_quantity(product_quantity)
        except IndexError:
            return Handler().indexerror()

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.id).annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        )
