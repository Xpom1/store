from django.db.models import Sum, F, Avg, Count
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework import mixins, filters
from rest_framework.response import Response
from .models import Product, Cart, Order, ProductPriceInfo
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductRetrieveSerializer, CartSerializer, ProductListSerializers, OrderSerializer
import pandas as pd

from .services.cart_operations import CartOperation
from .services.order_creator import OrderCreator
from .services.product_operations import ProductOperation
from .services.rating_feedback_service import RatingFeedbackService
from .services.sales_stats_service import SalesStatsService
from .tasks import load_data
from django.db.models import Prefetch
from .error_handler import Handler


class ProductViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     mixins.ListModelMixin, mixins.UpdateModelMixin, Handler):
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
        product_creator = ProductOperation()
        product_data, created = product_creator.create_product(request.data)
        if created:
            return Response(product_data)
        return self.created()

    @action(methods=['put'], detail=True)
    def attributes(self, request, pk=None):
        product_attribute_updater = ProductOperation()
        product = self.get_object()
        updated_data = product_attribute_updater.update_attributes(product, request.data.get('attributes'))
        return Response(updated_data)


class CartListAPIViewAdmin(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return Cart.objects.all().annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        ).prefetch_related('products__product')


class LoadProductsFromExcelAPIView(generics.CreateAPIView, Handler):
    permission_classes = (IsAdminUser,)

    def create(self, request, **kwargs):
        data_ = pd.read_excel(request.FILES['upload_file']).to_dict('records')
        load_data.delay(data_)
        return self.success()


class CartViewSet(viewsets.ModelViewSet, Handler):
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return CartOperation(user=request.user, queryset=queryset).list_cart()

    @action(methods=['put'], detail=False)
    def change(self, request):
        data = request.data
        product_id = data.get('product_id')
        command = data.get('command').strip()
        queryset = self.get_queryset()
        cart_change_service = CartOperation(user=request.user, queryset=queryset)
        success, cart_product = cart_change_service.change_product_quantity(product_id, command)

        if success is True:
            return self.success_with_data(data=cart_product)
        elif success is False:
            return self.deleted()
        elif success is None:
            if cart_product is None:
                return self.unrecognized_command()
            else:
                return self.indexerror()

    @action(methods=['delete'], detail=False)
    def remove(self, request):
        data = request.data
        product_id = data.get('product_id')
        deleted, _ = self.get_queryset()[0].products.filter(product_id=product_id).delete()
        if deleted:
            return self.success()
        else:
            return self.indexerror()

    @action(methods=['post'], detail=False)
    def add(self, request):
        data = request.data
        try:
            product_id = data.get('product_id')
            product_quantity = Product.objects.get(id=product_id).quantity
            quantity = int(data.get('quantity'))
            if 0 < quantity <= product_quantity:
                self.get_queryset()[0].products.create()
                return self.success()
            return self.max_quantity(product_quantity)
        except IndexError:
            return self.indexerror()

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.id).annotate(
            total_sum=Sum(F('products__quantity') * F('product__price'))
        )


class ListCreateOrderAPIView(generics.ListCreateAPIView, Handler):
    serializer_class = OrderSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).order_by('-timestamp')

    def create(self, request, *args, **kwargs):
        order_creator = OrderCreator(request.user)
        success, message = order_creator.create_order()
        if success:
            return self.success()
        elif message == "Not enough balance":
            return self.not_enough_balance()
        else:
            return self.cart_empty()


class CreateUpdateDestroyRatingFeedbackAPIView(generics.UpdateAPIView, generics.CreateAPIView, generics.DestroyAPIView,
                                               Handler):
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        service = RatingFeedbackService(user=request.user)
        status, _ = service.create_rating_feedback(
            product_id=self.kwargs.get('pk'),
            rating=request.data.get('rating'),
            feedback=request.data.get('feedback'),
            parent_id=request.data.get('parent_id')
        )
        return self.handle_response(status)

    def update(self, request, *args, **kwargs):
        service = RatingFeedbackService(user=request.user)
        status, _ = service.update_rating_feedback(
            rating_feedback_id=request.data.get('id'),
            feedback=request.data.get('feedback'),
            product_id=self.kwargs.get('pk'),
        )
        return self.handle_response(status)

    def destroy(self, request, *args, **kwargs):
        service = RatingFeedbackService(user=request.user)
        status, _ = service.delete_rating_feedback(
            rating_feedback_id=request.data.get('id'),
            product_id=self.kwargs.get('pk')
        )
        return self.handle_response(status)

    def handle_response(self, status):
        if status == 'success':
            return self.success()
        elif status == 'not_purchased':
            return self.not_purchased_product()
        elif status == 'rating_exists':
            return self.rating_already_exist()
        elif status == 'rating_not_exist':
            return self.rating_not_exist()


class SaleStatsAPIView(generics.ListAPIView):
    permission_classes = (IsAdminUser,)

    def list(self, request, *args, **kwargs):
        data = request.data
        type_ = data.get('type')
        filter_ = data.get('filter')
        value = data.get('value', '[]')

        stats_service = SalesStatsService()
        stats = stats_service.get_stats(type_, filter_, value)

        return Response(stats)
