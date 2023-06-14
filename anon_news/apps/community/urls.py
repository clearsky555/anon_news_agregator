from django.urls import path

from apps.blog.views import PostCreateView

from apps.community import views


urlpatterns = [
    path('create/', views.CommunityCreateView.as_view(), name='new_community'),
    path('all/', views.AllCommunitiesView.as_view(), name='all_communities'),
    path('popular/', views.PopularCommunitiesView.as_view(), name='popular_communities'),
    path('my-communities/', views.my_communities, name='my_communities'),
    path('forbidden/', views.forbidden, name='forbidden'),

    path('membership/accept/<slug:community_slug>/<int:user_id>/', views.Accept.as_view(), name='accept'),
    path('membership/decline/<slug:community_slug>/<int:user_id>/', views.Decline.as_view(), name='decline'),

    path('membership/<slug:community_slug>/application-processing/', views.ApllicationProcessingView.as_view(), name='application_processing'),
    path('membership/<slug:community_slug>/', views.membership, name='membership_application'),

    path('<slug:community_slug>/', views.CommunityDetailView.as_view(), name='community_detail'),

    path('subscribe/<slug:community_slug>/', views.subscribe_community, name='subscribe_community'),
    path('unsubscribe/<slug:community_slug>/', views.unsubscribe_community, name='unsubscribe_community'),

    path('<slug:community_slug>/post-create/', PostCreateView.as_view(), name='post_create'),

    path('<slug:community_slug>/subscribers/', views.SubscribersListView.as_view(), name='subscribers'),

    path('<slug:community_slug>/exclude/<int:user_id>/', views.ExcludeUserView.as_view(), name='exclude_user'),
]
