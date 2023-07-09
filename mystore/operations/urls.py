from rest_framework import routers
from django.urls import path
from operations.views import CartViewSet, ProductViewSet, CartListAPIView

router = routers.DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('carts/', CartListAPIView.as_view()),
]

urlpatterns += router.urls
