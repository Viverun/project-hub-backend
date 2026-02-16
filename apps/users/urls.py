from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.UserProfileView.as_view(), name='user-profile'),
    path('<uuid:user_id>', views.UserDetailView.as_view(), name='user-detail'),
    path('github/<str:username>', views.GitHubStatsView.as_view(), name='github-stats'),
    path('search', views.UserSearchView.as_view(), name='user-search'),
]
