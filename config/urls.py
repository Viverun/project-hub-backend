"""
Main URL Configuration for Project Hub API
"""

from django.urls import path, include

urlpatterns = [
    path('api/auth/', include('apps.auth.urls')),
    path('api/user/', include('apps.users.urls')),
    path('api/projects/', include('apps.projects.urls')),
    path('api/teams/', include('apps.teams.urls')),
    path('api/events/', include('apps.events.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
    path('api/health/', include('apps.core.urls')),
]
