from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status as http_status
from core.mongo_orm import ValidationError, MultipleValidationErrors

def custom_exception_handler(exc, context):
    """
    Кастомний handler для обробки винятків MongoDB ORM.
    Інтегрується з Django REST Framework.
    """
    # Спочатку викликаємо стандартний DRF handler
    response = exception_handler(exc, context)
    
    # Якщо DRF не обробив помилку
    if response is None:
        # Обробляємо ValidationError з MongoDB ORM
        if isinstance(exc, ValidationError):
            return Response({
                'error': str(exc),
                'detail': exc.message,
                'field': exc.field if hasattr(exc, 'field') else None
            }, status=http_status.HTTP_400_BAD_REQUEST)
        
        # Обробляємо MultipleValidationErrors
        if isinstance(exc, MultipleValidationErrors):
            return Response({
                'error': 'Помилка валідації',
                'errors': exc.errors
            }, status=http_status.HTTP_400_BAD_REQUEST)
    
    return response
