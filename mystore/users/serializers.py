from rest_framework import serializers
from django.contrib.auth.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    balance = serializers.FloatField(source='userbalance.balance', read_only=True)

    class Meta:
        model = User
        fields = ('username', "first_name", "last_name", "email", "balance", "is_staff", "last_login", "date_joined")
