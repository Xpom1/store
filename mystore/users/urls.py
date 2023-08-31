from django.urls import path

from .views import UserAPIView, UserBalanceAPIView

urlpatterns = [
    path('register/', UserAPIView.as_view()),
    path('balance/', UserBalanceAPIView.as_view())
]
