# apps/api/views/user_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.main.models import User
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
