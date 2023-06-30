from django.urls import path

from apps.blog import views


urlpatterns = [
    path('', views.PostListView.as_view(), name='all'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/comment/save/<int:post_id>/', views.save_comment_form, name='save_comment'),

    path('post/comment/save/<int:post_id>/<int:comment_id>/', views.save_comment_reply_form, name='save_comment_reply'),

    path('post/like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/dislike/<int:post_id>/', views.dislike_post, name='dislike_post'),

    path('post/comment/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('post/comment/dislike/<int:comment_id>/', views.dislike_comment, name='dislike_comment'),

    path('new/', views.PostListView.as_view(), name='new_posts'),
    path('popular/', views.PopularPostListView.as_view(), name='popular_posts'),
    path('discuss/', views.DiscussPostListView.as_view(), name='discuss_posts'),

    path('notifications/', views.NotificationView.as_view(), name='notifications'),

    path('notifications/mark-as-read/', views.mark_notifications_as_read, name='mark_notifications_as_read'),

    path('post/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    path('post/comment/delete/<int:post_id>/<int:comment_id>', views.delete_comment, name='delete_comment'),

    path('post/permaban/<int:pk>/', views.post_permaban, name='post_permaban'),
    path('comment/permaban/<int:pk>/', views.comment_permaban, name='comment_permaban'),
]