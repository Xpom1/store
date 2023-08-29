from rest_framework import routers
from django.urls import path
from operations.views import CartViewSet, ProductViewSet, CartListAPIViewAdmin, CreateListOrderViewSets, \
    LoadDataFromExcel

router = routers.DefaultRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'products', ProductViewSet, basename='products')
router.register(r'order', CreateListOrderViewSets, basename='order')

urlpatterns = [
    path('carts/', CartListAPIViewAdmin.as_view()),
    path('load_data/', LoadDataFromExcel.as_view({'post': 'load_data'}))
]

urlpatterns += router.urls
