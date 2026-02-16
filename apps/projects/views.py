from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Project
from .serializers import ProjectSerializer
from django.db.models import Q

User = get_user_model()


class ProjectCreateListView(APIView):
    def get(self, request):
        """List all projects with optional filtering"""
        query = request.query_params.get('search', '')
        status_filter = request.query_params.get('status', '')
        tech_stack = request.query_params.get('techStack', '')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))

        projects = Project.objects.all()

        if query:
            projects = projects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        if status_filter:
            projects = projects.filter(status=status_filter)
        if tech_stack:
            tech_list = tech_stack.split(',')
            for tech in tech_list:
                projects = projects.filter(tech_stack__contains=tech)

        total = projects.count()
        start = (page - 1) * limit
        end = start + limit
        projects = projects[start:end]

        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        })

    def post(self, request):
        """Create a new project (authenticated)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            user = User.objects.get(id=request.user_id)
            serializer = ProjectSerializer(data=request.data)

            if serializer.is_valid():
                project = serializer.save(owner=user)
                return Response({'success': True, 'data': ProjectSerializer(project, context={'request': request}).data}, status=status.HTTP_201_CREATED)
            return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ProjectDetailView(APIView):
    def get(self, request, project_id):
        """Get project details"""
        try:
            project = Project.objects.get(id=project_id)
            serializer = ProjectSerializer(project, context={'request': request})
            return Response({'success': True, 'data': serializer.data})
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, project_id):
        """Update project (owner only)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            project = Project.objects.get(id=project_id)
            if str(project.owner.id) != str(request.user_id):
                return Response({'success': False, 'message': 'Only owner can update'}, status=status.HTTP_403_FORBIDDEN)

            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                project = serializer.save()
                return Response({'success': True, 'data': ProjectSerializer(project, context={'request': request}).data})
            return Response({'success': False, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, project_id):
        """Delete project (owner only)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            project = Project.objects.get(id=project_id)
            if str(project.owner.id) != str(request.user_id):
                return Response({'success': False, 'message': 'Only owner can delete'}, status=status.HTTP_403_FORBIDDEN)

            project.delete()
            return Response({'success': True, 'message': 'Project deleted successfully'})
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


class ProjectBookmarkView(APIView):
    def post(self, request, project_id):
        """Toggle bookmark on project (authenticated)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            project = Project.objects.get(id=project_id)
            user_id_str = str(request.user_id)

            if user_id_str in project.bookmarked_by:
                project.bookmarked_by.remove(user_id_str)
            else:
                project.bookmarked_by.append(user_id_str)

            project.save()
            serializer = ProjectSerializer(project, context={'request': request})
            return Response({'success': True, 'data': serializer.data, 'is_bookmarked': user_id_str in project.bookmarked_by})
        except Project.DoesNotExist:
            return Response({'success': False, 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


class UserProjectsView(APIView):
    def get(self, request):
        """Get user's projects (authenticated)"""
        if not hasattr(request, 'user_id'):
            return Response({'success': False, 'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            projects = Project.objects.filter(owner_id=request.user_id)
            serializer = ProjectSerializer(projects, many=True, context={'request': request})
            return Response({'success': True, 'data': serializer.data})
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
