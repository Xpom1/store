from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import mixins

from .models import Product, Cart_Product
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
    permission_classes = (IsAdminOrReadOnly,)


class CartAPIView(generics.ListAPIView):
    queryset = Cart_Product.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)


class CartAPIUpdate(generics.ListAPIView, mixins.UpdateModelMixin):
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)

    def get_queryset(self):
        return Cart_Product.objects.filter(user=self.request.user.id)
