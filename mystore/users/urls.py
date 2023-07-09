from django.urls import path

from .views import UserViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'create', 'get': 'retrieve'}))
]
