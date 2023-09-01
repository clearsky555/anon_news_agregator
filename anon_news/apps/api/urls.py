from django.urls import path
from apps.api import views
from apps.accounts import views as user_views

from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

schema_view = get_schema_view(
   openapi.Info(
      title="anon_news",
      default_version='v1',
      description="anon app",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="admin@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('docs/', schema_view.with_ui('swagger')),
    path('v1/users/', views.UserListAPIView.as_view(), name='users_api'),
    path('v1/posts/', views.PostListAPIView.as_view()),

    path('v1/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', user_views.CreateUserAPIView.as_view()),
]