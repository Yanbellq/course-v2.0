from django.urls import path
from ..views import crm_views, user_views

urlpatterns = [
    # API для клієнтської сторони
    path('register/', user_views.customer_registration, name='api_register'),
    # path('login/', crm_views.customer_login, name='api_login'),
    # path('profile/', crm_views.api_profile, name='api_profile'),
]