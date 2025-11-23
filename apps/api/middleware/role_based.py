# apps/api/middleware/role_based.py

from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse


class RoleBasedAccessMiddleware:
    """
    Middleware для перевірки ролей користувача
    
    Правила доступу:
    - /api/admin/* - тільки admin
    - /api/user/* - всі авторизовані
    - /crm/admin/* - тільки admin (через session)
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        path = request.path
        
        # Правила для API (перевіряємо request.user з JWT)
        api_admin_paths = ['/api/admin/', '/api/analytics/']
        api_user_paths = ['/api/user/profile/', '/api/products/']
        
        # Правила для Web (перевіряємо session)
        web_admin_paths = ['/crm/admin/', '/crm/analytics/']
        
        # Перевірка API admin endpoints
        if any(path.startswith(p) for p in api_admin_paths):
            if not hasattr(request, 'user'):
                return JsonResponse({
                    'success': False,
                    'error': 'Authentication required',
                    'code': 'NO_AUTH'
                }, status=401)
            
            if request.user.role != 'admin':
                return JsonResponse({
                    'success': False,
                    'error': 'Admin access required',
                    'code': 'FORBIDDEN'
                }, status=403)
        
        # Перевірка Web admin endpoints
        if any(path.startswith(p) for p in web_admin_paths):
            admin_id = request.session.get('admin_id')
            
            if not admin_id:
                return redirect('crm:login')
            
            # Отримуємо адміна з MongoDB
            from apps.main.models import User
            admin = User.find_by_id(admin_id)
            
            if not admin or admin.role != 'admin':
                return HttpResponseForbidden('Admin access required')
        
        response = self.get_response(request)
        return response
