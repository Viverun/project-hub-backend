from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.core.authentication import generate_tokens
import bcrypt
import jwt
from django.conf import settings

from .serializers import RegisterSerializer, LoginSerializer, AuthResponseSerializer, UserSerializer

User = get_user_model()


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(
                username=serializer.validated_data['email'],
                email=serializer.validated_data['email'],
                first_name=serializer.validated_data['name'],
                password=serializer.validated_data['password']
            )

            access_token, refresh_token = generate_tokens(str(user.id))

            response_data = {
                'success': True,
                'data': {
                    'user': UserSerializer(user).data,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email__iexact=serializer.validated_data['email'])

            if not user.check_password(serializer.validated_data['password']):
                return Response({
                    'success': False,
                    'message': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)

            access_token, refresh_token = generate_tokens(str(user.id))

            response_data = {
                'success': True,
                'data': {
                    'user': UserSerializer(user).data,
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Invalid email or password'
            }, status=status.HTTP_401_UNAUTHORIZED)


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({
                'success': False,
                'message': 'Refresh token is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)

            access_token, _ = generate_tokens(str(user.id))

            return Response({
                'success': True,
                'data': {
                    'access_token': access_token,
                }
            }, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            return Response({
                'success': False,
                'message': 'Refresh token has expired'
            }, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return Response({
                'success': False,
                'message': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    def post(self, request):
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
