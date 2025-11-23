# apps/api/middleware/jwt_web.py

import jwt
from django.conf import settings
from django.shortcuts import redirect
from apps.main.models import User
from datetime import datetime


class JWTWebAuthenticationMiddleware:
    """
    Автентифікація для Django WEB (CRM) через JWT у cookies.
    Додає request.user для /crm/* шляхом декодування access_token.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Працюємо тільки з CRM (WEB) сторінками
        if path.startswith("/crm/"):
            token = request.COOKIES.get("access_token")

            if not token:
                request.user = None
                # Use session instead of messages (messages middleware not ready yet)
                request.session['auth_message'] = 'Please log in to access this page.'
                request.session['auth_message_type'] = 'warning'
                return redirect("/auth/?next=" + path)

            try:
                payload = jwt.decode(
                    token,
                    settings.JWT_SECRET_KEY,
                    algorithms=[settings.JWT_ALGORITHM]
                )

                user = User.find_by_id(payload["user_id"])

                if not user or not user.is_active:
                    request.user = None
                    # Use session instead of messages
                    request.session['auth_message'] = 'Your account is inactive or invalid. Please log in again.'
                    request.session['auth_message_type'] = 'warning'
                    response = redirect("/auth/?next=" + path)
                    response.delete_cookie('access_token')
                    response.delete_cookie('refresh_token')
                    return response

                # Створюємо user object (як ти робиш у API)
                user_obj = type("User", (), {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_authenticated": True
                })()

                request.user = user_obj

            except jwt.ExpiredSignatureError:
                # Token expired - try to refresh it
                request.user = None
                refresh_token = request.COOKIES.get("refresh_token")
                
                if refresh_token:
                    try:
                        refresh_payload = jwt.decode(
                            refresh_token,
                            settings.JWT_SECRET_KEY,
                            algorithms=[settings.JWT_ALGORITHM]
                        )
                        user = User.find_by_id(refresh_payload["user_id"])
                        if user and user.is_active:
                            # Generate new access token
                            from apps.api.authentication.user_jwt_authentication import create_access_token
                            new_access_token = create_access_token(user)
                            
                            # Redirect with new token in cookie
                            response = redirect(path)
                            # Використовуємо secure=True для HTTPS (production на Render)
                            is_secure = not settings.DEBUG
                            response.set_cookie(
                                'access_token',
                                new_access_token,
                                httponly=True,
                                secure=is_secure,
                                samesite="Lax",
                                max_age=settings.JWT_ACCESS_TOKEN_LIFETIME
                            )
                            # Use session instead of messages
                            request.session['auth_message'] = 'Your session has been refreshed.'
                            request.session['auth_message_type'] = 'info'
                            return response
                    except Exception:
                        pass
                
                # No valid refresh token - redirect to login
                # Use session instead of messages
                request.session['auth_message'] = 'Your session has expired. Please log in again.'
                request.session['auth_message_type'] = 'warning'
                response = redirect("/auth/?next=" + path)
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                return response
                
            except Exception as e:
                # Other JWT errors (invalid token, etc.)
                request.user = None
                # Use session instead of messages
                request.session['auth_message'] = 'Authentication error. Please log in again.'
                request.session['auth_message_type'] = 'error'
                response = redirect("/auth/?next=" + path)
                response.delete_cookie('access_token')
                response.delete_cookie('refresh_token')
                return response

        return self.get_response(request)
