# apps/api/middleware/rate_limit.py

from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime


class RateLimitMiddleware:
    """
    Middleware для обмеження кількості запитів
    
    Ліміти:
    - API: 200 запитів/хвилину
    - Auth endpoints: 50 запитів/хвилину (захист від brute-force)
    - Default: 300 запитів/хвилину
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Налаштування лімітів
        self.limits = {
            'api': {'requests': 200, 'period': 60},
            'auth': {'requests': 50, 'period': 60},  # Збільшено з 10 до 50
            'default': {'requests': 300, 'period': 60},
        }
    
    def __call__(self, request):
        # Визначаємо тип endpoint
        path = request.path
        
        if path.startswith('/api/user/auth/'):
            limit_type = 'auth'
        elif path.startswith('/api/'):
            limit_type = 'api'
        else:
            limit_type = 'default'
        
        # Отримуємо IP
        ip = self.get_client_ip(request)
        
        # Ключ для cache
        cache_key = f"rate_limit:{limit_type}:{ip}"
        
        # Отримуємо ліміт
        limit_config = self.limits[limit_type]
        max_requests = limit_config['requests']
        period = limit_config['period']
        
        # Перевіряємо кількість запитів
        requests_data = cache.get(cache_key, {'count': 0, 'reset_at': None})
        
        # Якщо ліміт перевищено
        if requests_data['count'] >= max_requests:
            retry_after = period
            
            # Для API повертаємо JSON
            if path.startswith('/api/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Too many requests',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': retry_after,
                    'limit': max_requests,
                    'period': period
                }, status=429)
            
            # Для Web повертаємо HTML
            from django.http import HttpResponse
            return HttpResponse(
                f'<h1>429 Too Many Requests</h1>'
                f'<p>Ліміт: {max_requests} запитів за {period} секунд</p>'
                f'<p>Спробуйте через {retry_after} секунд</p>',
                status=429
            )
        
        # Збільшуємо лічильник
        requests_data['count'] += 1
        cache.set(cache_key, requests_data, period)
        
        response = self.get_response(request)
        
        # Додаємо headers для rate limit
        response['X-RateLimit-Limit'] = str(max_requests)
        response['X-RateLimit-Remaining'] = str(max_requests - requests_data['count'])
        response['X-RateLimit-Reset'] = str(period)
        
        return response
    
    def get_client_ip(self, request):
        """Отримати реальний IP клієнта (враховуючи proxy)"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
