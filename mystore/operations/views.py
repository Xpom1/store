import json
from django.db.models import Sum, F, Q, Avg, Count
from django.db.models.functions import Least
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import mixins, filters
from rest_framework.response import Response
from eav.models import Attribute, Value
from django.db import transaction
from .models import Product, Cart, CartProduct, OrderProduct, Order, Rating_Feedback, ProductPriceInfo
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductRetrieveSerializer, CartSerializer, ProductListSerializers, OrderSerializer
import pandas as pd
from .tasks import load_data
from django.db.models import Prefetch
from datetime import date


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

    def not_enough_balance(self):
        return Response({"status": "error", "message": "Not enough balance"})

    def cart_empty(self):
        return Response({"status": "error", "message": "Cart is empty"})

    def not_purchased_product(self):
        return Response({"status": "error", "message": "Вы не можете оставить отзыв на товар, который еще не заказали"})

    def rating_already_exist(self):
        return Response({"status": "error", "message": "У вас уже есть отзыв на этот товар, вы можете его изменить"})

    def rating_not_exist(self):
        return Response({"status": "error", "message": "Вы не можете менять/удалять рэйтинг, тк еще не поставили его."})

    def feedback_must_be_present(self):
        return Response({"status": "error", "message": "Чтобы поменять комментарий, вы должны указать комментарий"})

    def incorrect_time(self):
        return Response({"status": "error", "message": "Чтобы получить статистику вы должны указать значения времени "
                                                       "для полей start и end"})

    def incorrect_command(self):
        return Response({"status": "error", "message": "Нет такого типа группировки, обратитесь в Swagger"})


class ProductViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.ListModelMixin, mixins.UpdateModelMixin):
    serializer_class = ProductRetrieveSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'price']
    queryset = Product.objects.annotate(rating=Avg('rating_feedback__rating'),
                                        count=Count('rating_feedback__rating')).prefetch_related(
        Prefetch('productpriceinfo_set', queryset=ProductPriceInfo.objects.order_by('timestamp')))

    def partial_update(self, request, *args, **kwargs):
        data = request.data
        if data.get('price') and float(data.get('price')) != ProductPriceInfo.objects.filter(
                product_id=kwargs.get('pk')).last().price:
            ProductPriceInfo.objects.create(price=data.get('price'), product_id=kwargs.get('pk'))
        return super().partial_update(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return ProductListSerializers
        return self.serializer_class

    def create(self, request, *args, **kwargs):
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
            return Response(ProductRetrieveSerializer(prod).data)
        return Handler().created()

    @action(methods=['put'], detail=False)
    def attributes(self, request, pk=None):
        data = request.data
        prod = self.get_queryset()[0]
        attributes = json.loads(data.get('attributes'))
        Value.objects.filter(entity_id=prod.eav_values.pk_val).delete()
        for key, val in attributes.items():
            Attribute.objects.get_or_create(slug=key, name=key, datatype=Attribute.TYPE_JSON)
            prod.eav.__setattr__(key, val)
        prod.save()
        return Response(ProductRetrieveSerializer(prod).data)


class CartListAPIViewAdmin(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Cart.objects.all().annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        ).prefetch_related('products__product')


class LoadProductsFromExcelAPIView(generics.CreateAPIView):
    permission_classes = (IsAdminUser,)

    def create(self, request, **kwargs):
        data_ = pd.read_excel(request.FILES['upload_file']).to_dict('records')
        load_data.delay(data_)
        return Handler().success()


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        queryset[0].products.filter(product__quantity=0).delete()
        per = queryset[0].products.all().select_related('product')
        for product in per:
            product.quantity = min(product.product.quantity, product.quantity)
        queryset[0].products.bulk_update(per, ['quantity'])
        return Response(serializer.data)

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
                self.get_queryset()[0].products.create()
                return Handler().success()
            return Handler().max_quantity(product_quantity)
        except IndexError:
            return Handler().indexerror()

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.id).annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        )


class ListCreateOrderAPIView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-timestamp')

    @transaction.atomic
    def create(self, request):
        user = self.request.user
        user_balance = user.userbalance.balance
        user_cart = user.cart
        total_cost = Cart.objects.filter(customer=user).aggregate(
            total_sum=Sum(F('products__quantity') * F('product__price'))).get('total_sum')
        if total_cost:
            if user_balance > total_cost:
                user.userbalance.remove_balance(total_cost)
                order_id = Order.objects.create(customer=user, total_cost=total_cost).id
                order_products = user_cart.products.all()
                for product in order_products:
                    product.order_id = order_id
                    product.price = product.product.price
                OrderProduct.objects.bulk_create(order_products)
                for i in order_products:
                    Product.objects.filter(id=i.product.id).update(quantity=F('quantity') - i.quantity)
                order_products.delete()
                return Handler().success()
            else:
                return Handler().not_enough_balance()
        else:
            return Handler().cart_empty()


class CreateUpdateDestroyRatingFeedbackAPIView(generics.UpdateAPIView, generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        data = request.data
        commented_id = data.get('commented_id')
        user = self.request.user
        if not commented_id:
            product = Product.objects.get(id=self.kwargs.get('pk'))
            if not Rating_Feedback.objects.filter(user=user, product_id=product).exists():
                if OrderProduct.objects.filter(order_id__customer=user, product_id=product).exists():
                    data = request.data
                    Rating_Feedback.objects.create(user=user, product=product,
                                                   rating=data.get('rating'),
                                                   feedback=data.get('feedback'))
                    return Handler().success()
                return Handler().not_purchased_product()
            return Handler().rating_already_exist()
        else:
            Rating_Feedback.objects.create(feedback=data.get('feedback'), user=user, commented_id=commented_id)
            return Handler().success()

    def update(self, request, *args, **kwargs):
        data = request.data
        id_ = data.get('id')
        if not id_:
            user = self.request.user
            product = Product.objects.get(id=self.kwargs.get('pk'))
            rating = Rating_Feedback.objects.filter(user=user, product_id=product)
            if rating:
                data = request.data
                rating.update(rating=data.get('rating'), feedback=data.get('feedback'))
                return Handler().success()
            return Handler().rating_not_exist()
        else:
            feedback = data.get('feedback')
            if feedback:
                Rating_Feedback.objects.filter(id=id_).update(feedback=data.get('feedback'))
                return Handler().success()
            return Handler().feedback_must_be_present()

    def destroy(self, request, *args, **kwargs):
        data = request.data
        id_ = data.get('id')
        if not id_:
            user = self.request.user
            product = Product.objects.get(id=self.kwargs.get('pk'))
            rating = Rating_Feedback.objects.filter(user=user, product_id=product)
            if rating:
                rating.delete()
                return Handler().success()
            return Handler().rating_not_exist()
        else:
            Rating_Feedback.objects.filter(id=id_).delete()
            return Handler().success()


class SaleStatsAPIView(generics.ListCreateAPIView):
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        grouping = {'category': 'product__category', 'users': 'customer', 'time': 'timestamp__date',
                    'cost': 'orderproduct__price'}
        filtering = {'category': 'product__category', 'users': 'customer', 'time': 'timestamp__date__range',
                     'cost': 'orderproduct__price__range'}
        data = request.data
        type_ = data.get('type')
        filter_ = data.get('filter')
        value = json.loads(data.get('value'))
        # Записать словарик и сделать проверку
        print(Order.objects.filter(**{filtering.get(filter_): value}).values(grouping.get(type_)))

        if type_ == 'category':
            a = Order.objects.values('product__category').annotate(
                total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                count_sale=Sum('orderproduct__quantity'), Avg_price=Avg('orderproduct__price'))
            b = Order.objects.values(
                'product__category').annotate(Avg_rating=Avg('product__rating_feedback__rating'))
            # Вопрос: Алгорит сбора данных по группам всегда одинаковый или как у set()? Обязательно ли сортировать?
            a = sorted(a, key=lambda x: x['product__category'] if x['product__category'] is not None else 0)
            b = sorted(b, key=lambda x: x['product__category'] if x['product__category'] is not None else 0)
            for i in range(len(a)):
                a[i]['Avg_rating'] = b[i].get('Avg_rating')
            return Response(a)
        elif type_ == 'time':
            start = pd.to_datetime(data.get('start'), dayfirst=True)
            end = pd.to_datetime(data.get('end'), dayfirst=True)
            if start and end:
                name = 'timestamp__date'
                a = Order.objects.values('timestamp__date').filter(timestamp__date__range=[start, end]).annotate(
                    total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                    count_sale=Sum('orderproduct__quantity'), Avg_price=Avg('orderproduct__price'))
                b = Order.objects.values('timestamp__date').filter(timestamp__date__range=[start, end]).annotate(
                    Avg_rating=Avg('product__rating_feedback__rating'))
                a = sorted(a, key=lambda x: x['timestamp__date'])
                b = sorted(b, key=lambda x: x['timestamp__date'])
                for i in range(len(a)):
                    a[i]['Avg_rating'] = b[i].get('Avg_rating')
                return Response(a)
            return Handler().incorrect_time()
        elif type_ == 'cost':
            a = Order.objects.values('orderproduct__price').annotate(
                total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                count_sale=Sum('orderproduct__quantity'), Avg_price=Avg('orderproduct__price'))
            b = Order.objects.values('orderproduct__price').annotate(Avg_rating=Avg('product__rating_feedback__rating'))
            a = sorted(a, key=lambda x: x['orderproduct__price'])
            b = sorted(b, key=lambda x: x['orderproduct__price'])
            for i in range(len(a)):
                a[i]['Avg_rating'] = b[i].get('Avg_rating')
            return Response(a)
        elif type_ == 'users':
            a = Order.objects.values('customer').annotate(
                total_cost_=Sum(F('orderproduct__price') * F('orderproduct__quantity')),
                count_sale=Sum('orderproduct__quantity'), Avg_price=Avg('orderproduct__price'))
            b = Order.objects.values('customer').annotate(Avg_rating=Avg('product__rating_feedback__rating'))
            a = sorted(a, key=lambda x: x['customer'])
            b = sorted(b, key=lambda x: x['customer'])
            for i in range(len(a)):
                a[i]['Avg_rating'] = b[i].get('Avg_rating')
            return Response(a)
        return Handler().incorrect_command()
