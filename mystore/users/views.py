from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User

from users.serializers import UserInfoSerializer


class LoginViewSet(viewsets.ModelViewSet):
    @action(methods=['post'], detail=False)
    def info(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        user = User.objects.get(username=username)
        if user is None:
            return Response({"response": "No User exist"})
        if user.check_password(password):
            return Response(UserInfoSerializer(user).data)

    @action(methods=['put'], detail=False)
    def create_users(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        try:
            created_user = User.objects.create_user(username=username, password=password, email=email)
            return Response(UserInfoSerializer(created_user).data)
        except:
            return Response({'response': 'This user already exists'})



