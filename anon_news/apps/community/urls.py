from django.urls import path

from apps.blog.views import PostCreateView

from apps.community import views

urlpatterns = [
    path('create/', views.CommunityCreateView.as_view(), name='new_community'),
    path('all/', views.AllCommunitiesView.as_view(), name='all_communities'),
    path('<slug:community_slug>/', views.CommunityDetailView.as_view(), name='community_detail'),
    path('subscribe/<slug:community_slug>/', views.subscribe_community, name='subscribe_community'),
    path('unsubscribe/<slug:community_slug>/', views.unsubscribe_community, name='unsubscribe_community'),
    path('<slug:community_slug>/post-create/', PostCreateView.as_view(), name='post_create'),
]