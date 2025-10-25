from django.urls import path

from apps.main import views

app_name = 'urls'

urlpatterns = [
    path('', views.dashboard, name='index'),
    path('auth/', views.auth, name='auth'),
    path('categories/', views.categories, name='categories'),
    path('categories/<str:category>/', views.categories, name='categories'),


]