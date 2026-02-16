import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class JWTAuthentication(BaseAuthentication):
    """JWT Token Authentication"""

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        try:
            token = auth_header[7:]
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            user_id = payload.get('user_id')

            if not user_id:
                raise AuthenticationFailed('Invalid token')

            # Return user_id in request for later use
            request.user_id = user_id
            return (user_id, None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')


def generate_tokens(user_id):
    """Generate access and refresh tokens"""
    access_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        'iat': datetime.utcnow(),
    }

    refresh_payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS),
        'iat': datetime.utcnow(),
    }

    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return access_token, refresh_token
