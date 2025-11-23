from django.urls import path
from apps.main import views as v

app_name = 'main'

urlpatterns = [
    # Головна сторінка
    path("", v.dashboard, name="index"),
    path("auth/", v.auth, name="auth"),
    path("profile/", v.profile, name="profile"),
    path("categories/", v.categories, name="categories"),
    path('product/<str:product_id>/', v.product_detail, name='product_detail'),
]
