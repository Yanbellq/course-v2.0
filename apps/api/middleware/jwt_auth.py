# apps/api/middleware/jwt_auth.py

import jwt
from django.http import JsonResponse
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from apps.api.authentication.user_jwt_authentication import MongoJWTAuthentication
from apps.main.models import User


class JWTAuthenticationMiddleware:
    """
    Middleware для автоматичної JWT автентифікації
    
    Застосовується тільки до API endpoints (/api/*)
    Django templates використовують sessions
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = MongoJWTAuthentication()
    
    def __call__(self, request):
        # Публічні API endpoints (без токена)
        public_api_paths = [
            '/api/user/auth/register/',
            '/api/user/auth/login/',
            '/api/user/auth/refresh/',
            '/api/categories',
            '/api/products',
            '/api/search',
            '/api/docs/',  # API документація
        ]
        
        # Django web endpoints (використовують sessions, не JWT)
        web_paths = [
            '/admin/',
            '/crm/',
            '/static/',
            '/media/',
        ]
        
        path = request.path
        
        # Перевірка чи це API endpoint
        is_api = path.startswith('/api/')
        is_public_api = any(path.startswith(p) for p in public_api_paths)
        is_web = any(path.startswith(p) for p in web_paths)
        
        # Якщо це API і НЕ публічний - перевіряємо JWT
        if is_api and not is_public_api:
            try:
                # Спочатку перевіряємо Authorization header
                user_auth = self.jwt_auth.authenticate(request)
                
                # Якщо немає в header, перевіряємо cookies (для /api/analytics/)
                if user_auth is None and path.startswith('/api/analytics/'):
                    token = request.COOKIES.get('access_token')
                    if token:
                        try:
                            payload = jwt.decode(
                                token,
                                settings.JWT_SECRET_KEY,
                                algorithms=[settings.JWT_ALGORITHM]
                            )
                            user = User.find_by_id(payload.get('user_id'))
                            if user and user.is_active:
                                user_obj = type('User', (), {
                                    'id': str(user.id),
                                    'username': user.username,
                                    'email': user.email,
                                    'role': user.role,
                                    'is_active': user.is_active,
                                    'is_authenticated': True,
                                })()
                                user_auth = (user_obj, None)
                        except Exception:
                            pass
                
                if user_auth is None:
                    return JsonResponse({
                        'success': False,
                        'error': 'Authentication required',
                        'code': 'NO_TOKEN'
                    }, status=401)
                
                # Додаємо користувача в request
                request.user, _ = user_auth
                request.auth_type = 'jwt'  # Помічаємо тип автентифікації
                
            except AuthenticationFailed as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e),
                    'code': 'INVALID_TOKEN'
                }, status=401)
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication error',
                    'details': str(e) if request.META.get('DEBUG') else None
                }, status=500)
        
        response = self.get_response(request)
        return response
