from django.shortcuts import render

from rest_framework.generics import ListAPIView
from apps.api.serializers import UserSerializer, PostSerializer
from apps.accounts.models import User
from apps.blog.models import Post
from rest_framework.pagination import PageNumberPagination


class UserAPIListPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class UserListAPIView(ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = UserAPIListPagination


class PostListAPIView(ListAPIView):
    serializer_class = PostSerializer
    queryset = Post.objects.all()