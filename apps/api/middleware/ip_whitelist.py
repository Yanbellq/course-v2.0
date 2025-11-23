# apps/api/middleware/ip_whitelist.py

import logging
from django.http import JsonResponse, HttpResponseForbidden
from django.conf import settings

logger = logging.getLogger('api')  # ← ДОДАНО!


class IPWhitelistMiddleware:
    """
    Middleware для обмеження доступу за IP
    
    Використовуйте для admin панелі або критичних endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Дозволені IP (можна винести в settings)
        self.whitelist = getattr(settings, 'IP_WHITELIST', [
            '127.0.0.1',
            'localhost',
        ])
        
        # Шляхи з обмеженням
        self.restricted_paths = [
            '/admin/',
            '/api/admin/',
        ]
    
    def __call__(self, request):
        path = request.path
        
        # Перевіряємо чи шлях обмежений
        is_restricted = any(path.startswith(p) for p in self.restricted_paths)
        
        if is_restricted:
            client_ip = self.get_client_ip(request)
            
            if client_ip not in self.whitelist:
                logger.warning(f"IP {client_ip} blocked from accessing {path}")
                
                if path.startswith('/api/'):
                    return JsonResponse({
                        'success': False,
                        'error': 'Access denied',
                        'code': 'IP_BLOCKED'
                    }, status=403)
                
                return HttpResponseForbidden('Access denied')
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Отримати IP клієнта"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
