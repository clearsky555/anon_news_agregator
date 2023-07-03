from django.shortcuts import render

from rest_framework.generics import ListAPIView
from apps.api.serializers import UserSerializer
from apps.accounts.models import User


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()


