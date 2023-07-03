from django.urls import path
from apps.api import views


urlpatterns = [
    path('users/', views.UserListAPIView.as_view()),
]