from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import mixins, filters

from .models import Product, Cart
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductListSerializer, CartSerializer, ProductListViewCart


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


class CartAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)


class CartAPIUpdate(generics.ListAPIView, mixins.UpdateModelMixin):
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        return Cart.objects.filter(customer=self.request.user.id)

# def total_cost(user_is):
#