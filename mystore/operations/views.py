from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Product, Cart
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin
from .serializers import ProductSerializer, CartSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAdminOrReadOnly,)


class CartAPIView(generics.ListAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAdminUser,)


class CartAPIUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsOwnerOrAdmin,)