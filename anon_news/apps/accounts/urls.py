from django.urls import path
from apps.accounts import views


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/done/', views.RegisterDoneView.as_view(), name='register_done'),
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('profile/<int:pk>/', views.Profile.as_view(), name='profile'),
    path('profile/save_image/', views.save_image, name='save_image'),

    path('permaban/<int:pk>/', views.permaban, name='permaban'),

    path('adduser/<int:pk>/', views.AddUser.as_view(), name='add_user_in_chat'),
    path('adduser2/<str:chat_name>/<int:user_id>/', views.adduser2, name='add_user_in_chat_2'),

    path('send_message/<int:user_id>/', views.send_message, name='send_message'),
]