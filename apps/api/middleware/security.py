# apps/api/middleware/security.py

import re
import logging
from django.http import JsonResponse, HttpResponseBadRequest

logger = logging.getLogger('api')  # ← ДОДАНО!


class SecurityMiddleware:
    """
    Middleware для додаткових перевірок безпеки
    
    Перевіряє:
    - SQL injection спроби
    - XSS атаки
    - Підозрілі patterns
    - Заблоковані user agents
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b.*\b=\b.*\bor\b)",
            r"(drop\s+table)",
            r"(insert\s+into)",
            r"(delete\s+from)",
            r"(update\s+.*\bset\b)",
            r"(exec\s*\()",
            r"(;.*--)",
        ]
        
        # XSS patterns
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"onerror\s*=",
            r"onload\s*=",
        ]
        
        # Заблоковані user agents (боти, скрапери)
        self.blocked_agents = [
            'sqlmap',
            'nikto',
            'nmap',
            'masscan',
        ]
    
    def __call__(self, request):
        # Перевірка User-Agent
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        
        if any(blocked in user_agent for blocked in self.blocked_agents):
            logger.warning(f"Blocked suspicious user agent: {user_agent}")
            
            if request.path.startswith('/api/'):
                return JsonResponse({
                    'success': False,
                    'error': 'Access denied',
                    'code': 'BLOCKED_AGENT'
                }, status=403)
            
            return HttpResponseBadRequest('Access denied')
        
        # Перевірка SQL injection
        query_string = request.META.get('QUERY_STRING', '').lower()
        path = request.path.lower()
        
        for pattern in self.sql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE) or \
               re.search(pattern, path, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {request.path}")
                
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid request',
                        'code': 'SECURITY_VIOLATION'
                    }, status=400)
                
                return HttpResponseBadRequest('Invalid request')
        
        # Перевірка XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {request.path}")
                
                if request.path.startswith('/api/'):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid request',
                        'code': 'SECURITY_VIOLATION'
                    }, status=400)
                
                return HttpResponseBadRequest('Invalid request')
        
        response = self.get_response(request)
        
        # Додаємо security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        
        return response
