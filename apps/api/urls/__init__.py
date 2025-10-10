# apps/api/urls.py
from django.urls import path, include

from ..views import crm_views, user_views

app_name = 'api'

urlpatterns = [
    path('', include('apps.api.urls.crm_urls')),
    path('', include('apps.api.urls.user_urls')),
]