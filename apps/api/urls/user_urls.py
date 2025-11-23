from django.urls import path
from apps.api.views import user_views as views_auth

app_name = 'user'

urlpatterns = [
    # Автентифікація
    path('auth/register/', views_auth.register, name='register'),
    path('auth/login/', views_auth.login, name='login'),
    path('auth/logout/', views_auth.logout, name='logout'),
    path('auth/refresh/', views_auth.refresh_token, name='refresh_token'),
    path('auth/me/', views_auth.get_current_user, name='current_user'),
    
    

]
