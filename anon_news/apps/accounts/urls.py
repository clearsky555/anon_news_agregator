from django.urls import path
from apps.accounts import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/done/', views.RegisterDoneView.as_view(), name='register_done'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
]