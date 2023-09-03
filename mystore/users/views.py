from django.db.models import F
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User

from users.serializers import UserInfoSerializer

from rest_framework.permissions import IsAuthenticated


class UserAPIView(generics.CreateAPIView):
    serializer_class = UserInfoSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        return self.request.user

    def create(self, request, **kwargs):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        try:
            created_user = User.objects.create_user(username=username, password=password, email=email)
            return Response(UserInfoSerializer(created_user).data)
        except:
            return Response({'response': 'This user already exists'})


class RefillUserBalanceAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def create(self, request, **kwargs):
        data = request.data
        deposit = float(data.get('deposit'))
        return Response({'balance': self.request.user.userbalance.add_balance(deposit)})
