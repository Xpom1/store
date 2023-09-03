from django.urls import path

from .views import UserAPIView, RefillUserBalanceAPIView

urlpatterns = [
    path('register/', UserAPIView.as_view()),
    path('balance/', RefillUserBalanceAPIView.as_view())
]
