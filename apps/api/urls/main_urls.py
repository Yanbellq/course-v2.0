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
    
    # Newsletter
    path('newsletter/subscribe/', mv.newsletter_subscribe, name='newsletter_subscribe'),
    
    # Supplier Validation
    path('suppliers/check-email/', mv.check_supplier_email_unique, name='check_supplier_email_unique'),
    path('suppliers/check-phone/', mv.check_supplier_phone_unique, name='check_supplier_phone_unique'),
    
    # Product Category Validation
    path('categories/check-name/', mv.check_category_name_unique, name='check_category_name_unique'),
    path('categories/check-slug/', mv.check_category_slug_unique, name='check_category_slug_unique'),
    path('categories/check-image-url/', mv.check_category_image_url_unique, name='check_category_image_url_unique'),
    
    # Product Validation
    path('products/check-name/', mv.check_product_name_unique, name='check_product_name_unique'),
    path('products/check-image-url/', mv.check_product_image_url_unique, name='check_product_image_url_unique'),
    
    # Employee Validation
    path('employees/check-email/', mv.check_employee_email_unique, name='check_employee_email_unique'),
    path('employees/check-phone/', mv.check_employee_phone_unique, name='check_employee_phone_unique'),
]
