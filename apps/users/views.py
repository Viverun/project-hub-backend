from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
import requests
from django.conf import settings

User = get_user_model()


def _safe_user_payload(user):
    teams_joined_value = getattr(user, 'teams_joined', 0)
    if hasattr(teams_joined_value, 'count'):
        try:
            teams_joined_value = teams_joined_value.count()
        except Exception:
            teams_joined_value = 0

    github_username_value = getattr(user, 'github_username', None)
    if github_username_value is None:
        github_username_value = getattr(user, 'last_name', None) or None

    return {
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'name': getattr(user, 'first_name', '') or user.username,
        'profile_picture_url': getattr(user, 'profile_picture_url', None),
        'bio': getattr(user, 'bio', ''),
        'github_username': github_username_value,
        'leetcode_username': getattr(user, 'leetcode_username', None),
        'skills': getattr(user, 'skills', []),
        'interests': getattr(user, 'interests', []),
        'projects_created': getattr(user, 'projects_created', 0),
        'projects_completed': getattr(user, 'projects_completed', 0),
        'teams_joined': teams_joined_value,
    }


class UserProfileView(APIView):
    def get(self, request):
        """Get user profile (authenticated)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=request.user_id)
            return Response({
                'success': True,
                'data': _safe_user_payload(user)
            })
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request):
        """Update user profile (authenticated)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=request.user_id)

            # Update allowed fields
            for field in ['first_name', 'bio', 'profile_picture_url', 'github_url', 'linkedin_url', 'skills', 'interests', 'github_username', 'leetcode_username']:
                if field in request.data and hasattr(user, field):
                    setattr(user, field, request.data[field])

            if 'github_username' in request.data and not hasattr(user, 'github_username'):
                user.last_name = request.data.get('github_username') or ''

            user.save()
            return Response({
                'success': True,
                'data': _safe_user_payload(user)
            })
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserDetailView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id):
        """Get user by ID"""
        try:
            user = User.objects.get(id=user_id)
            return Response({
                'success': True,
                'data': _safe_user_payload(user)
            })
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class GitHubStatsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, username):
        """Get GitHub stats for user"""
        try:
            headers = {}
            if settings.GITHUB_API_TOKEN:
                headers['Authorization'] = f'token {settings.GITHUB_API_TOKEN}'

            response = requests.get(f'{settings.GITHUB_API_URL}/users/{username}', headers=headers)

            if response.status_code != 200:
                return Response({'success': False, 'message': 'GitHub user not found'}, status=status.HTTP_404_NOT_FOUND)

            data = response.json()
            return Response({
                'success': True,
                'data': {
                    'username': data.get('login'),
                    'public_repos': data.get('public_repos'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'joined_at': data.get('created_at'),
                }
            })
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserSearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        """Search users"""
        query = request.query_params.get('q', '')
        limit = int(request.query_params.get('limit', 10))

        if not query:
            return Response({'success': False, 'message': 'Query parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        users = User.objects.filter(username__icontains=query)[:limit]
        return Response({
            'success': True,
            'data': [{
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'profile_picture_url': getattr(user, 'profile_picture_url', None),
            } for user in users]
        })
