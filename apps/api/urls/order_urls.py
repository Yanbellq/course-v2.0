# apps/api/urls/order_urls.py

from django.urls import path
from apps.api.views import order_views

app_name = 'order'

urlpatterns = [
    path('create/', order_views.create_order, name='create_order'),
]

