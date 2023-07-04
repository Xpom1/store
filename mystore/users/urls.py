from django.urls import path

from .views import LoginViewSet

urlpatterns = [
    path('', LoginViewSet.as_view({'post': 'info', 'put': 'create_users'}))
]
