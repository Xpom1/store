from django.urls import path

from .views import UserViewSet, UserBalanceViewsSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'create', 'get': 'retrieve'})),
    path('balance/', UserBalanceViewsSet.as_view({'post': 'add_balance'}))
]
