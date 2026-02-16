from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectCreateListView.as_view(), name='project-list-create'),
    path('<uuid:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<uuid:project_id>/bookmark', views.ProjectBookmarkView.as_view(), name='project-bookmark'),
    path('my-projects/', views.UserProjectsView.as_view(), name='user-projects'),
]
