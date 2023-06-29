import json
from django.db.models import Sum, F
from django.db.models.functions import Least
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import mixins, filters
from rest_framework.response import Response
from eav.models import Attribute

from .models import Product, Cart, CartProduct
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductListSerializer, CartSerializer, ProductListViewCart


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

    def created(self):
        return Response({'value': 'The product has already been created'})


# viewsets заменя
class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductListSerializer
    permission_classes = (IsAdminOrReadOnly,)
    # Тут он должен обрабатывать /api/v1/products/1/attributes/
    @action(methods=['put'], detail=False)
    def attributes(self, request):
        data = request.data
        attributes = data.get('attributes')
        print(attributes, self.get_queryset())
        return Handler().success()

    # def put(self, request, *args, **kwargs):
    #     return self.update(request, *args, **kwargs)

    def get_queryset(self):
        return Product.objects.filter(id=self.kwargs['pk'])


class ProductViewSmallerVersion(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductListViewCart
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'price']
    permission_classes = (IsAdminOrReadOnly,)

    @action(methods=['post'], detail=False)
    def add(self, request):
        data = request.data

        name = data.get('name')
        description = data.get('description')
        price = ''.join(data.get('price').split())
        quantity = data.get('quantity')
        category = data.get('category')
        attributes = json.loads(data.get('attributes'))
        prod, created = Product.objects.get_or_create(name=name, defaults={'description': description, 'price': price,
                                                                           'quantity': quantity})
        if created:
            if category:
                prod.category.set(category)
            for key, val in attributes.items():
                Attribute.objects.get_or_create(slug=key, name=key, datatype=Attribute.TYPE_JSON)
                prod.eav.__setattr__(key, val)
            prod.save()
            return Response(ProductListSerializer(prod).data)
        return Handler().created()


class ManyCartAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Cart.objects.all().annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        )


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
            cart_product = self.get_queryset()[0].products.filter(product_id=product_id)
            if command.isdigit():
                cart_product.update(quantity=Least(product_quantity, int(command)))
                return Handler().success_with_data(data=cart_product)
            elif command == 'add':
                cart_product.update(quantity=Least(product_quantity, F('quantity') + 1))
                return Handler().success_with_data(data=cart_product)
            elif command == 'reduce':
                if cart_product[0].quantity > 1:
                    cart_product.update(quantity=Least(product_quantity, F('quantity') - 1))
                    return Handler().success_with_data(data=cart_product)
                else:
                    cart_product.delete()
                    return Handler().deleted()
            else:
                return Handler().unrecognized_command()
        except IndexError:
            return Handler().indexerror()

    @action(methods=['delete'], detail=False)
    def remove(self, request):
        data = request.data
        product_id = data.get('product_id')
        deleted, _ = self.get_queryset()[0].products.filter(product_id=product_id).delete()
        if deleted:
            return Handler().success()
        else:
            return Handler().indexerror()

    @action(methods=['post'], detail=False)
    def add(self, request):
        data = request.data
        # Обработать ошибку добавления товара с таким же Id
        # Добавить еще колическво товара
        try:
            product_id = data.get('product_id')
            cart_id = self.get_queryset()[0].id
            product_quantity = Product.objects.get(id=product_id).quantity
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
