from rest_framework import routers
from django.urls import path
from operations.views import CartAPIView, ProductViewSmallerVersion, ProductViewSet, ManyCartAPIView

router = routers.DefaultRouter()
router.register(r'cart', CartAPIView, basename='cart')
router.register(r'products', ProductViewSmallerVersion, basename='products')

urlpatterns = [
    path('products/<int:pk>/', ProductViewSet.as_view({'get': 'list'})),
    path('products/<int:pk>/attributes/', ProductViewSet.as_view({'put': 'attributes'})),

    path('carts/', ManyCartAPIView.as_view()),
]

urlpatterns += router.urls