from django.urls import path, include
from apps.api.views.analytics_views import analytics_api

app_name = 'analytics'

urlpatterns = [
    path('', analytics_api, name="analytics_api"),
]