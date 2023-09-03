from rest_framework import routers
from django.urls import path
from operations.views import CartViewSet, ProductViewSet, CartListAPIViewAdmin, ListCreateOrderAPIView, \
    LoadProductsFromExcelAPIView

router = routers.DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('carts/', CartListAPIViewAdmin.as_view()),
    path('load_data/', LoadProductsFromExcelAPIView.as_view()),
    path('order/', ListCreateOrderAPIView.as_view(), name='order')
]

urlpatterns += router.urls
