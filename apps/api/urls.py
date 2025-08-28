# apps/api/urls.py
from django.urls import path, include
from . import views

app_name = 'api'

urlpatterns = [
    # API для отримання даних
    path('suppliers/', views.api_suppliers_list, name='api_suppliers_list'),
    path('suppliers/add/', views.api_supplier_add, name='api_supplier_add'),
    path('suppliers/<str:supplier_id>/', views.api_supplier_detail, name='api_supplier_detail'),

    path('customers/', views.api_customers_list, name='api_customers_list'),
    path('customers/add/', views.api_customer_add, name='api_customer_add'),
    path('customers/<str:customer_id>/', views.api_customer_detail, name='api_customer_detail'),

    path('products/', views.api_products_list, name='api_products_list'),
    path('products/add/', views.api_product_add, name='api_product_add'),
    path('products/<str:product_id>/', views.api_product_detail, name='api_product_detail'),
    path('products/categories/', views.api_categories_list, name='api_categories_list'),

    path('contracts/', views.api_contracts_list, name='api_contracts_list'),
    path('contracts/<str:contract_id>/', views.api_contract_detail, name='api_contract_detail'),

    path('sales/', views.api_sales_list, name='api_sales_list'),
    path('sales/<str:sale_id>/', views.api_sale_detail, name='api_sale_detail'),

    path('repairs/', views.api_repairs_list, name='api_repairs_list'),
    path('repairs/<str:repair_id>/', views.api_repair_detail, name='api_repair_detail'),

    path('warranties/', views.api_warranties_list, name='api_warranties_list'),
    path('services/', views.api_services_list, name='api_services_list'),
    path('custom-pc/', views.api_custom_pc_list, name='api_custom_pc_list'),
    path('employees/', views.api_employees_list, name='api_employees_list'),

    # API для звітів
    path('reports/suppliers-products/', views.api_report_suppliers_products, name='api_report_suppliers_products'),
    path('reports/customers-by-manufacturer/', views.api_report_customers_by_manufacturer,
         name='api_report_customers_by_manufacturer'),
    path('reports/warranty-repairs/', views.api_report_warranty_repairs, name='api_report_warranty_repairs'),
    path('reports/sales-analytics/', views.api_report_sales_analytics, name='api_report_sales_analytics'),
    path('reports/components-by-price/', views.api_report_components_by_price, name='api_report_components_by_price'),
    path('reports/suppliers-repair-frequency/', views.api_report_suppliers_repair_frequency,
         name='api_report_suppliers_repair_frequency'),
    path('reports/custom-pc-components/', views.api_report_custom_pc_components,
         name='api_report_custom_pc_components'),
    path('reports/supplier-deliveries/', views.api_report_supplier_deliveries, name='api_report_supplier_deliveries'),
    path('reports/contracts-period/', views.api_report_contracts_period, name='api_report_contracts_period'),
    path('reports/supplier-by-contract/', views.api_report_supplier_by_contract,
         name='api_report_supplier_by_contract'),
]