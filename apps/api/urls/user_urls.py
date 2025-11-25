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
    path('auth/change-password/', views_auth.change_password, name='change_password'),
    path('auth/forgot-password/', views_auth.forgot_password, name='forgot_password'),
    path('auth/reset-password/', views_auth.reset_password, name='reset_password'),
    
    # Валідація унікальності
    path('check-email/', views_auth.check_email_unique, name='check_email_unique'),
    path('check-username/', views_auth.check_username_unique, name='check_username_unique'),
]
