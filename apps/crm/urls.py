from django.urls import path, include
from apps.crm import views
from apps.crm import queries_views

app_name = 'crm'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Suppliers
    path('suppliers/', views.suppliers_list, name='suppliers_list'),
    path('suppliers/create/', views.suppliers_create, name='suppliers_create'),
    path('suppliers/<str:pk>/edit/', views.suppliers_edit, name='suppliers_edit'),
    path('suppliers/<str:pk>/delete/', views.suppliers_delete, name='suppliers_delete'),

    # Contracts
    path('contracts/', views.contracts_list, name='contracts_list'),
    path('contracts/create/', views.contracts_create, name='contracts_create'),
    path('contracts/<str:pk>/edit/', views.contracts_edit, name='contracts_edit'),
    path('contracts/<str:pk>/delete/', views.contracts_delete, name='contracts_delete'),

    # Supplies
    path('supplies/', views.supplies_list, name='supplies_list'),
    path('supplies/create/', views.supplies_create, name='supplies_create'),
    path('supplies/<str:pk>/edit/', views.supplies_edit, name='supplies_edit'),
    path('supplies/<str:pk>/delete/', views.supplies_delete, name='supplies_delete'),

    # Employees
    path('employees/', views.employees_list, name='employees_list'),
    path('employees/create/', views.employees_create, name='employees_create'),
    path('employees/<str:pk>/edit/', views.employees_edit, name='employees_edit'),
    path('employees/<str:pk>/delete/', views.employees_delete, name='employees_delete'),

    # Sales
    path('sales/', views.sales_list, name='sales_list'),
    path('sales/create/', views.sales_create, name='sales_create'),
    path('sales/<str:pk>/edit/', views.sales_edit, name='sales_edit'),
    path('sales/<str:pk>/delete/', views.sales_delete, name='sales_delete'),

    # Repairs
    path('repairs/', views.repairs_list, name='repairs_list'),
    path('repairs/create/', views.repairs_create, name='repairs_create'),
    path('repairs/<str:pk>/edit/', views.repairs_edit, name='repairs_edit'),
    path('repairs/<str:pk>/delete/', views.repairs_delete, name='repairs_delete'),

    # Deliveries
    path('deliveries/', views.deliveries_list, name='deliveries_list'),
    path('deliveries/create/', views.deliveries_create, name='deliveries_create'),
    path('deliveries/<str:pk>/edit/', views.deliveries_edit, name='deliveries_edit'),
    path('deliveries/<str:pk>/delete/', views.deliveries_delete, name='deliveries_delete'),

    # Users (list)
    path('users/', views.users_list, name='users_list'),
    
    # Product Categories
    path('product-categories/', views.product_categories_list, name='product_categories_list'),
    path('product-categories/create/', views.product_categories_create, name='product_categories_create'),
    path('product-categories/<str:pk>/edit/', views.product_categories_edit, name='product_categories_edit'),
    path('product-categories/<str:pk>/delete/', views.product_categories_delete, name='product_categories_delete'),
    
    # Products
    path('products/', views.products_list, name='products_list'),
    path('products/create/', views.products_create, name='products_create'),
    path('products/<str:pk>/edit/', views.products_edit, name='products_edit'),
    path('products/<str:pk>/delete/', views.products_delete, name='products_delete'),
    
    # Queries
    path('queries/', queries_views.queries_index, name='queries_index'),
    path('queries/1-suppliers-products/', queries_views.query1_suppliers_with_products, name='query1_suppliers'),
    path('queries/1-components-multiple/', queries_views.query1_components_multiple_suppliers, name='query1_components'),
    path('queries/2-customers-manufacturer/', queries_views.query2_customers_by_manufacturer, name='query2_customers'),
    path('queries/3-warranty-returned/', queries_views.query3_warranty_repairs_returned, name='query3_returned'),
    path('queries/3-warranty-completed/', queries_views.query3_warranty_repairs_completed, name='query3_completed'),
    path('queries/3-warranty-in-progress/', queries_views.query3_warranty_repairs_in_progress, name='query3_in_progress'),
    path('queries/4-max-revenue/', queries_views.query4_max_revenue_by_month, name='query4_max_revenue'),
    path('queries/4-revenue-type/', queries_views.query4_revenue_by_product_type_last_week, name='query4_revenue_type'),
    path('queries/4-sales-employee/', queries_views.query4_sales_by_employee, name='query4_sales_employee'),
    path('queries/5-components-price/', queries_views.query5_components_by_price, name='query5_components'),
    path('queries/6-suppliers-repairs/', queries_views.query6_suppliers_by_repair_frequency, name='query6_suppliers'),
    path('queries/7-custom-build/', queries_views.query7_custom_build_components, name='query7_custom_build'),
    path('queries/8-product-supplies/', queries_views.query8_product_supplies_by_period, name='query8_supplies'),
    path('queries/9-contracts-period/', queries_views.query9_contracts_by_period, name='query9_contracts_period'),
    path('queries/9-contracts-count/', queries_views.query9_contracts_count_by_supplier, name='query9_contracts_count'),
    path('queries/10-supplier-contract/', queries_views.query10_supplier_by_contract_number, name='query10_supplier'),
]
