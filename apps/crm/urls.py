# apps/crm/urls.py
from django.urls import path
from . import views

app_name = 'crm'

urlpatterns = [
    # Головна сторінка
    path('', views.index, name='index'),

    # Постачальники
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/add/', views.supplier_add, name='supplier_add'),
    path('suppliers/<str:supplier_id>/', views.supplier_detail, name='supplier_detail'),

    # Клієнти
    path('customers/', views.customers_list, name='customers_list'),
    path('customers/add/', views.customer_add, name='customer_add'),
    path('customers/<str:customer_id>/', views.customer_detail, name='customer_detail'),

    # Товари
    path('products/', views.products_list, name='products_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('products/categories/', views.categories_list, name='categories_list'),

    # Договори
    path('contracts/', views.contracts_list, name='contracts_list'),
    path('contracts/add/', views.contract_add, name='contract_add'),
    path('contracts/<str:contract_id>/', views.contract_detail, name='contract_detail'),

    # Поставки
    path('supplies/', views.supplies_list, name='supplies_list'),
    path('supplies/add/', views.supply_add, name='supply_add'),

    # Продажі
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/add/', views.sale_add, name='sale_add'),
    path('sales/<str:sale_id>/', views.sale_detail, name='sale_detail'),

    # Ремонти
    path('repairs/', views.repairs_list, name='repairs_list'),
    path('repairs/add/', views.repair_add, name='repair_add'),
    path('repairs/<str:repair_id>/', views.repair_detail, name='repair_detail'),

    # Гарантії
    path('warranties/', views.warranties_list, name='warranties_list'),
    path('warranties/<str:warranty_id>/', views.warranty_detail, name='warranty_detail'),

    # Послуги
    path('services/', views.services_list, name='services_list'),
    path('services/add/', views.service_add, name='service_add'),
    path('services/<str:service_id>/', views.service_detail, name='service_detail'),

    # Збірка ПК
    path('custom-pc/', views.custom_pc_list, name='custom_pc_list'),
    path('custom-pc/add/', views.custom_pc_add, name='custom_pc_add'),
    path('custom-pc/<str:pc_id>/', views.custom_pc_detail, name='custom_pc_detail'),

    # Співробітники
    path('employees/', views.employees_list, name='employees_list'),
    path('employees/add/', views.employee_add, name='employee_add'),

    # Звіти
    path('reports/', views.reports, name='reports'),
    path('reports/suppliers-products/', views.report_suppliers_products, name='report_suppliers_products'),
    path('reports/customers-by-manufacturer/', views.report_customers_by_manufacturer,
         name='report_customers_by_manufacturer'),
    path('reports/warranty-repairs/', views.report_warranty_repairs, name='report_warranty_repairs'),
    path('reports/sales-analytics/', views.report_sales_analytics, name='report_sales_analytics'),
    path('reports/components-by-price/', views.report_components_by_price, name='report_components_by_price'),
    path('reports/suppliers-repair-frequency/', views.report_suppliers_repair_frequency,
         name='report_suppliers_repair_frequency'),
    path('reports/custom-pc-components/', views.report_custom_pc_components, name='report_custom_pc_components'),
    path('reports/supplier-deliveries/', views.report_supplier_deliveries, name='report_supplier_deliveries'),
    path('reports/contracts-period/', views.report_contracts_period, name='report_contracts_period'),
    path('reports/supplier-by-contract/', views.report_supplier_by_contract, name='report_supplier_by_contract'),
]
