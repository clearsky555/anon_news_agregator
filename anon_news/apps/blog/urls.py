from django.urls import path

from apps.blog import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='all'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/comment/save/<int:post_id>/', views.save_comment_form, name='save_comment'),
    path('post/like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),

    path('post/comment/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('post/comment/dislike/<int:comment_id>/', views.dislike_comment, name='dislike_comment'),

]