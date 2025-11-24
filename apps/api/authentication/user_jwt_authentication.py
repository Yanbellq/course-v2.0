# apps/api/authentication/user_jwt_authentication.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.main.models import User


class MongoJWTAuthentication(BaseAuthentication):
    """Власна JWT автентифікація без rest_framework_simplejwt
    Підтримує токени з Authorization header або cookies
    """
    
    def authenticate(self, request):
        token = None
        
        # Спочатку перевіряємо Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            try:
                # Bearer <token>
                parts = auth_header.split()
                if len(parts) == 2 and parts[0].lower() == 'bearer':
                    token = parts[1]
            except Exception:
                pass
        
        # Якщо немає в header, перевіряємо cookies
        if not token:
            token = request.COOKIES.get('access_token')
        
        if not token:
            return None
        
        try:
            # Декодуємо JWT
            payload = jwt.decode(
                token, 
                settings.JWT_SECRET_KEY, 
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            user_id = payload.get('user_id')
            
            if not user_id:
                raise AuthenticationFailed('Invalid token payload')
            
            # Знаходимо користувача
            user = User.find_by_id(user_id)
            
            if not user or not user.is_active:
                raise AuthenticationFailed('User not found or inactive')
            
            # Повертаємо кастомний об'єкт користувача
            user_obj = type('User', (), {
                'id': str(user.id),
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'is_authenticated': True,
            })()
            
            return (user_obj, None)
        
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(f'Authentication error: {str(e)}')


def create_access_token(user, expires_delta=None):
    """Створити access token"""
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        'user_id': str(user.id),
        'username': user.username,
        'role': user.role,
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def create_refresh_token(user, expires_delta=None):
    """Створити refresh token"""
    if expires_delta is None:
        expires_delta = timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        'user_id': str(user.id),
        'exp': expire,
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }
    
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token


def get_tokens_for_user(user):
    """Генерація обох токенів"""
    return {
        'access': create_access_token(user),
        'refresh': create_refresh_token(user),
    }


def verify_refresh_token(token):
    """Перевірити refresh token"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        if payload.get('type') != 'refresh':
            raise jwt.InvalidTokenError('Not a refresh token')
        
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Refresh token has expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid refresh token')
