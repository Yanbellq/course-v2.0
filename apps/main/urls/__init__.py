from django.urls import path, include

app_name = 'main'

urlpatterns = [
    path('', include('apps.main.urls.urls')),
]