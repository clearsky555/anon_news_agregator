from django.urls import path
from apps.chat import views


urlpatterns = [
    # path('', views.DialoguesListView.as_view(), name='chat'),
    path("", views.index, name="index"),
    path("<str:room_name>/", views.room, name="room"),
    path('delete/<str:chat_name>/', views.delete_chat, name='delete_chat'), # ДОБАВИТЬ БЕЗОПАСНОСТЬ
]