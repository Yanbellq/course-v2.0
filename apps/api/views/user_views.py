# apps/api/views/user_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime

from apps.main.models import User, PasswordResetToken
from apps.api.serializers.user_serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer
)
from apps.api.authentication.user_jwt_authentication import (
    get_tokens_for_user,
    verify_refresh_token,
    create_access_token
)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Реєстрація"""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        
        return Response({
            'success': True,
            'message': 'Користувача успішно зареєстровано',
            'data': {
                'user': user.to_dict(),
                'tokens': tokens
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['POST'])
# @permission_classes([AllowAny])
# def login(request):
#     """Вхід"""
#     serializer = UserLoginSerializer(data=request.data)
    
#     if serializer.is_valid():
#         user = serializer.validated_data['user']
#         user.update_last_login()
        
#         tokens = get_tokens_for_user(user)
        
#         return Response({
#             'success': True,
#             'message': 'Успішний вхід',
#             'data': {
#                 'user': user.to_dict(),
#                 'tokens': tokens
#             }
#         }, status=status.HTTP_200_OK)
    
#     return Response({
#         'success': False,
#         'errors': serializer.errors
#     }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        user.update_last_login()

        tokens = get_tokens_for_user(user)

        response = Response({
            'success': True,
            'message': 'Успішний вхід',
            'data': {
                'user': user.to_dict(),
                'tokens': tokens
            }
        }, status=status.HTTP_200_OK)

        # 🟩 ВАЖЛИВО: Ставимо access-token у cookie
        from django.conf import settings
        # Використовуємо secure=True для HTTPS (production на Render)
        is_secure = not settings.DEBUG
        response.set_cookie(
            'access_token',
            tokens['access'],
            httponly=True,
            secure=is_secure,    # True для HTTPS (production)
            samesite="Lax",
            max_age=settings.JWT_ACCESS_TOKEN_LIFETIME  # 24 години
        )

        # Можеш додати refresh:
        response.set_cookie(
            'refresh_token',
            tokens['refresh'],
            httponly=True,
            secure=is_secure,    # True для HTTPS (production)
            samesite="Lax",
            max_age=60 * 60 * 24 * 7
        )

        return response

    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """Вихід (просто видаліть токени на клієнті)"""
    return Response({
        'success': True,
        'message': 'Успішний вихід'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """Оновлення access token"""
    try:
        refresh = request.data.get('refresh')
        
        if not refresh:
            return Response({
                'success': False,
                'error': 'Refresh token обов\'язковий'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payload = verify_refresh_token(refresh)
        user_id = payload.get('user_id')
        
        user = User.find_by_id(user_id)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Користувача не знайдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        new_access = create_access_token(user)
        
        return Response({
            'success': True,
            'data': {
                'access': new_access
            }
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """Поточний користувач"""
    try:
        user_id = request.user.id
        user = User.find_by_id(user_id)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Користувача не знайдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'data': user.to_dict()
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Зміна паролю"""
    try:
        user_id = request.user.id
        user = User.find_by_id(user_id)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Користувача не знайдено'
            }, status=status.HTTP_404_NOT_FOUND)
        
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Валідація
        if not current_password:
            return Response({
                'success': False,
                'error': 'Поточний пароль обов\'язковий'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({
                'success': False,
                'error': 'Новий пароль обов\'язковий'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({
                'success': False,
                'error': 'Новий пароль повинен містити мінімум 6 символів'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'error': 'Нові паролі не співпадають'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Перевірка поточного пароля
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'error': 'Невірний поточний пароль'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Перевірка, що новий пароль відрізняється від поточного
        if user.check_password(new_password):
            return Response({
                'success': False,
                'error': 'Новий пароль повинен відрізнятися від поточного'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Змінюємо пароль
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Пароль успішно змінено'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_password_reset_email(user, reset_url):
    """
    Відправляє email з інструкціями для відновлення пароля
    
    Args:
        user: Об'єкт користувача
        reset_url: URL для скидання пароля
    """
    import logging
    logger = logging.getLogger('api')
    
    # Перевірка налаштувань
    if not settings.EMAIL_HOST_USER:
        raise ValueError("EMAIL_HOST_USER не налаштовано в settings")
    if not settings.EMAIL_HOST_PASSWORD:
        raise ValueError("EMAIL_HOST_PASSWORD не налаштовано в settings")
    if not settings.DEFAULT_FROM_EMAIL:
        raise ValueError("DEFAULT_FROM_EMAIL не налаштовано в settings")
    
    subject = 'Відновлення пароля - Electronic Store'
    
    # Контекст для шаблону
    context = {
        'username': user.username,
        'reset_url': reset_url,
        'current_year': datetime.now().year,
    }
    
    # Рендеримо HTML та текстовий варіанти
    try:
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
    except Exception as e:
        logger.error(f"Failed to render email templates: {str(e)}")
        raise
    
    # Логуємо деталі перед відправкою
    logger.info(f"Sending email from {settings.DEFAULT_FROM_EMAIL} to {user.email}")
    logger.debug(f"Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    logger.debug(f"Email backend: {settings.EMAIL_BACKEND}")
    
    # Відправляємо email
    try:
        send_mail(
            subject=subject,
            message=plain_message,  # Текстова версія (для клієнтів без підтримки HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,  # HTML версія
            fail_silently=False,  # Викидає помилку, якщо не вдалось відправити
        )
        logger.info(f"Email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"SMTP error when sending email to {user.email}: {str(e)}", exc_info=True)
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """Запит на скидання пароля"""
    import logging
    logger = logging.getLogger('api')
    
    try:
        email = request.data.get('email')
        username = request.data.get('username')
        
        logger.info(f"Forgot password request received. Email: {email}, Username: {username}")
        
        # Валідація
        if not email and not username:
            logger.warning("Forgot password: no email or username provided")
            return Response({
                'success': False,
                'error': 'Вкажіть email або username'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Знаходимо користувача
        user = None
        if email:
            try:
                user = User.objects().filter(email=email).first()
                logger.info(f"User lookup by email {email}: {'found' if user else 'not found'}")
            except Exception as e:
                logger.error(f"Error looking up user by email: {str(e)}")
                pass
        
        if not user and username:
            try:
                user = User.objects().filter(username=username).first()
                logger.info(f"User lookup by username {username}: {'found' if user else 'not found'}")
            except Exception as e:
                logger.error(f"Error looking up user by username: {str(e)}")
                pass
        
        # Для безпеки завжди повертаємо успішну відповідь (навіть якщо користувача немає)
        # Це запобігає перевірці існування email/username
        if not user:
            logger.info("User not found, returning success message (security)")
            return Response({
                'success': True,
                'message': 'Якщо користувач з таким email/username існує, на пошту надіслано інструкції для скидання пароля'
            }, status=status.HTTP_200_OK)
        
        logger.info(f"User found: {user.username} ({user.email}), creating reset token")
        
        # Створюємо токен
        reset_token = PasswordResetToken.create_token(user)
        
        # Формуємо URL для скидання пароля
        reset_url = f"{request.scheme}://{request.get_host()}/auth/?token={reset_token.token}"
        
        logger.info(f"Reset token created. URL: {reset_url}")
        logger.info(f"Email settings check: USER={bool(settings.EMAIL_HOST_USER)}, PASSWORD={bool(settings.EMAIL_HOST_PASSWORD)}, BACKEND={settings.EMAIL_BACKEND}")
        
        # Відправляємо email
        try:
            # Перевіряємо налаштування email перед відправкою
            if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
                logger.warning(f"WARNING: EMAIL НЕ НАЛАШТОВАНО! EMAIL_HOST_USER: {bool(settings.EMAIL_HOST_USER)}, EMAIL_HOST_PASSWORD: {bool(settings.EMAIL_HOST_PASSWORD)}")
                logger.warning(f"Email backend: {settings.EMAIL_BACKEND}")
                logger.warning(f"EMAIL_HOST: {settings.EMAIL_HOST}, EMAIL_PORT: {settings.EMAIL_PORT}")
                
                # Виводимо токен в консоль як fallback (і в production теж)
                logger.warning(f"Password Reset Token for {user.email}: {reset_token.token}")
                logger.warning(f"Reset URL: {reset_url}")
            else:
                logger.info(f"[OK] Email settings OK. Attempting to send password reset email to {user.email}")
                send_password_reset_email(user, reset_url)
                logger.info(f"[OK] Password reset email sent successfully to {user.email}")
        except Exception as email_error:
            # Логуємо помилку, але не повідомляємо користувача (безпека)
            logger.error(f"[ERROR] Failed to send password reset email to {user.email}: {str(email_error)}", exc_info=True)
            logger.warning(f"Password Reset Token (fallback): {reset_token.token}")
            logger.warning(f"Reset URL (fallback): {reset_url}")
        
        return Response({
            'success': True,
            'message': 'Якщо користувач з таким email/username існує, на пошту надіслано інструкції для скидання пароля'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_password_reset_email(user, reset_url):
    """
    Відправляє email з інструкціями для відновлення пароля
    
    Args:
        user: Об'єкт користувача
        reset_url: URL для скидання пароля
    """
    import logging
    logger = logging.getLogger('api')
    
    # Перевірка налаштувань
    if not settings.EMAIL_HOST_USER:
        raise ValueError("EMAIL_HOST_USER не налаштовано в settings")
    if not settings.EMAIL_HOST_PASSWORD:
        raise ValueError("EMAIL_HOST_PASSWORD не налаштовано в settings")
    if not settings.DEFAULT_FROM_EMAIL:
        raise ValueError("DEFAULT_FROM_EMAIL не налаштовано в settings")
    
    subject = 'Відновлення пароля - Electronic Store'
    
    # Контекст для шаблону
    context = {
        'username': user.username,
        'reset_url': reset_url,
        'current_year': datetime.now().year,
    }
    
    # Рендеримо HTML та текстовий варіанти
    try:
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
    except Exception as e:
        logger.error(f"Failed to render email templates: {str(e)}")
        raise
    
    # Логуємо деталі перед відправкою
    logger.info(f"Sending email from {settings.DEFAULT_FROM_EMAIL} to {user.email}")
    logger.debug(f"Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    logger.debug(f"Email backend: {settings.EMAIL_BACKEND}")
    
    # Відправляємо email
    try:
        send_mail(
            subject=subject,
            message=plain_message,  # Текстова версія (для клієнтів без підтримки HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,  # HTML версія
            fail_silently=False,  # Викидає помилку, якщо не вдалось відправити
        )
        logger.info(f"Email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"SMTP error when sending email to {user.email}: {str(e)}", exc_info=True)
        raise


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request):
    """Скидання пароля за токеном"""
    try:
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        # Валідація
        if not token:
            return Response({
                'success': False,
                'error': 'Токен обов\'язковий'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_password:
            return Response({
                'success': False,
                'error': 'Новий пароль обов\'язковий'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 6:
            return Response({
                'success': False,
                'error': 'Пароль повинен містити мінімум 6 символів'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({
                'success': False,
                'error': 'Паролі не співпадають'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Перевіряємо токен
        user = PasswordResetToken.validate_token(token)
        
        if not user:
            return Response({
                'success': False,
                'error': 'Невірний або прострочений токен'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Знаходимо токен для позначення як використаний
        try:
            reset_token = PasswordResetToken.objects(token=token, used=False).first()
            if reset_token:
                reset_token.mark_as_used()
        except:
            pass  # Якщо не вдалось знайти токен, продовжуємо
        
        # Змінюємо пароль
        user.set_password(new_password)
        user.save()
        
        return Response({
            'success': True,
            'message': 'Пароль успішно змінено'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_password_reset_email(user, reset_url):
    """
    Відправляє email з інструкціями для відновлення пароля
    
    Args:
        user: Об'єкт користувача
        reset_url: URL для скидання пароля
    """
    import logging
    logger = logging.getLogger('api')
    
    # Перевірка налаштувань
    if not settings.EMAIL_HOST_USER:
        raise ValueError("EMAIL_HOST_USER не налаштовано в settings")
    if not settings.EMAIL_HOST_PASSWORD:
        raise ValueError("EMAIL_HOST_PASSWORD не налаштовано в settings")
    if not settings.DEFAULT_FROM_EMAIL:
        raise ValueError("DEFAULT_FROM_EMAIL не налаштовано в settings")
    
    subject = 'Відновлення пароля - Electronic Store'
    
    # Контекст для шаблону
    context = {
        'username': user.username,
        'reset_url': reset_url,
        'current_year': datetime.now().year,
    }
    
    # Рендеримо HTML та текстовий варіанти
    try:
        html_message = render_to_string('emails/password_reset.html', context)
        plain_message = render_to_string('emails/password_reset.txt', context)
    except Exception as e:
        logger.error(f"Failed to render email templates: {str(e)}")
        raise
    
    # Логуємо деталі перед відправкою
    logger.info(f"Sending email from {settings.DEFAULT_FROM_EMAIL} to {user.email}")
    logger.debug(f"Email host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
    logger.debug(f"Email backend: {settings.EMAIL_BACKEND}")
    
    # Відправляємо email
    try:
        send_mail(
            subject=subject,
            message=plain_message,  # Текстова версія (для клієнтів без підтримки HTML)
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,  # HTML версія
            fail_silently=False,  # Викидає помилку, якщо не вдалось відправити
        )
        logger.info(f"Email sent successfully to {user.email}")
    except Exception as e:
        logger.error(f"SMTP error when sending email to {user.email}: {str(e)}", exc_info=True)
        raise
