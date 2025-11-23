# apps/api/urls/main_urls.py

from django.urls import path
from apps.api.views import main_views as mv

urlpatterns = [
    # Категорії
    path('categories/', mv.list_product_categories, name='category-list'),
    path('categories/<str:pk>/get/', mv.get_product_category, name='category-detail'),
    path('categories/create/', mv.create_product_category, name='category-create'),
    path('categories/<str:pk>/update/', mv.update_product_category, name='category-update'),
    path('categories/<str:pk>/delete/', mv.delete_product_category, name='category-delete'),

    # Продукти
    path('products/', mv.list_products, name='list_products'),
    path('products/<str:pk>/get/', mv.get_product, name='get_product'),
    path('products/create/', mv.create_product, name='create_product'),
    path('products/<str:pk>/update/', mv.update_product, name='update_product'),
    path('products/<str:pk>/delete/', mv.delete_product, name='delete_product'),

    path('search/', mv.search_products, name='search_products'),
]
