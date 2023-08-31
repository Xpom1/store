from rest_framework import routers
from django.urls import path
from operations.views import CartViewSet, ProductViewSet, CartListAPIViewAdmin, CreateListOrderAPIView, \
    LoadDataFromExcelAPIView

router = routers.DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='products')

urlpatterns = [
    path('carts/', CartListAPIViewAdmin.as_view()),
    path('load_data/', LoadDataFromExcelAPIView.as_view()),
    path('order/', CreateListOrderAPIView.as_view(), name='order')
]

urlpatterns += router.urls
