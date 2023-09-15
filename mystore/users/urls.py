from django.urls import path
from rest_framework import routers
from .views import UserAPIView, RefillUserBalanceAPIView

router = routers.DefaultRouter()
router.register(r'register', UserAPIView, basename='register')

urlpatterns = [
    path('balance/', RefillUserBalanceAPIView.as_view())
]

urlpatterns += router.urls
