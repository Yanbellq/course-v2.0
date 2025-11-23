# apps/api/middleware/request_logging.py

import logging
import json
from datetime import datetime

logger = logging.getLogger('api')


class RequestLoggingMiddleware:
    """
    Middleware для детального логування запитів
    
    Логує:
    - Всі API запити
    - Час обробки
    - Користувача
    - IP адресу
    - Тіло запиту (для POST/PUT)
    - Статус відповіді
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Початок обробки
        start_time = datetime.now()
        
        # Отримуємо дані запиту
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Отримуємо користувача
        user_info = self.get_user_info(request)
        
        # Тіло запиту (тільки для POST/PUT/PATCH)
        request_body = None
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                request_body = json.loads(request.body.decode('utf-8'))
                # Приховуємо паролі
                if 'password' in request_body:
                    request_body['password'] = '***HIDDEN***'
                if 'password_confirm' in request_body:
                    request_body['password_confirm'] = '***HIDDEN***'
            except:
                request_body = None
        
        # Обробляємо запит
        response = self.get_response(request)
        
        # Час обробки
        duration = (datetime.now() - start_time).total_seconds()
        
        # Формуємо лог
        log_data = {
            'timestamp': start_time.isoformat(),
            'method': request.method,
            'path': request.path,
            'user': user_info,
            'ip': ip,
            'user_agent': user_agent[:100],  # Обрізаємо
            'status_code': response.status_code,
            'duration': f'{duration:.3f}s',
        }
        
        if request_body:
            log_data['request_body'] = request_body
        
        # Логуємо
        log_message = (
            f"[{request.method}] {request.path} | "
            f"User: {user_info} | "
            f"IP: {ip} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )
        
        # Рівень логування залежить від статусу
        if response.status_code >= 500:
            logger.error(log_message, extra=log_data)
        elif response.status_code >= 400:
            logger.warning(log_message, extra=log_data)
        else:
            logger.info(log_message, extra=log_data)
        
        return response
    
    def get_client_ip(self, request):
        """Отримати IP клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_user_info(self, request):
        """Отримати інформацію про користувача"""
        # JWT auth
        if hasattr(request, 'user') and hasattr(request.user, 'username'):
            return f"{request.user.username} ({request.user.role})"
        
        # Session auth
        admin_id = request.session.get('admin_id')
        if admin_id:
            return f"Admin:{admin_id}"
        
        return 'Anonymous'
