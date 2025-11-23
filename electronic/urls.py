from django.urls import path, include

urlpatterns = [
    path('', include('apps.main.urls')),
    path('crm/', include('apps.crm.urls')),
    path('api/', include('apps.api.urls')),
]
