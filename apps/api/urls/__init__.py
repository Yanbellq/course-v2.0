# apps/api/urls.py
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('', include('apps.api.urls.main_urls')),
    path('user/', include('apps.api.urls.user_urls')),
    path('analytics/', include('apps.api.urls.analytics_urls')),
    path('order/', include('apps.api.urls.order_urls')),
]