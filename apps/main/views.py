# apps/main/views.py
from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

def index(request):
    return render(request, 'index.html')

# Постачальники
def suppliers_list(request):
    return render(request, 'suppliers/list.html')

def supplier_add(request):
    return render(request, 'suppliers/add.html')

def supplier_detail(request, supplier_id):
    return render(request, 'suppliers/detail.html', {'supplier_id': supplier_id})

# Клієнти
def customers_list(request):
    return render(request, 'customers/list.html')

def customer_add(request):
    return render(request, 'customers/add.html')

def customer_detail(request, customer_id):
    return render(request, 'customers/detail.html', {'customer_id': customer_id})

# Товари
def products_list(request):
    return render(request, 'products/list.html')

def product_add(request):
    return render(request, 'products/add.html')

def product_detail(request, product_id):
    return render(request, 'products/detail.html', {'product_id': product_id})

def categories_list(request):
    return render(request, 'products/categories.html')

# Договори
def contracts_list(request):
    return render(request, 'contracts/list.html')

def contract_add(request):
    return render(request, 'contracts/add.html')

def contract_detail(request, contract_id):
    return render(request, 'contracts/detail.html', {'contract_id': contract_id})

# Поставки
def supplies_list(request):
    return render(request, 'supplies/list.html')

def supply_add(request):
    return render(request, 'supplies/add.html')

# Продажі
def sales_list(request):
    return render(request, 'sales/list.html')

def sale_add(request):
    return render(request, 'sales/add.html')

def sale_detail(request, sale_id):
    return render(request, 'sales/detail.html', {'sale_id': sale_id})

# Ремонти
def repairs_list(request):
    return render(request, 'repairs/list.html')

def repair_add(request):
    return render(request, 'repairs/add.html')

def repair_detail(request, repair_id):
    return render(request, 'repairs/detail.html', {'repair_id': repair_id})

# Гарантії
def warranties_list(request):
    return render(request, 'warranties/list.html')

def warranty_detail(request, warranty_id):
    return render(request, 'warranties/detail.html', {'warranty_id': warranty_id})

# Послуги
def services_list(request):
    return render(request, 'services/list.html')

def service_add(request):
    return render(request, 'services/add.html')

def service_detail(request, service_id):
    return render(request, 'services/detail.html', {'service_id': service_id})

# Збірка ПК
def custom_pc_list(request):
    return render(request, 'custom_pc/list.html')

def custom_pc_add(request):
    return render(request, 'custom_pc/add.html')

def custom_pc_detail(request, pc_id):
    return render(request, 'custom_pc/detail.html', {'pc_id': pc_id})

# Співробітники
def employees_list(request):
    return render(request, 'employees/list.html')

def employee_add(request):
    return render(request, 'employees/add.html')

# Звіти
def reports(request):
    return render(request, 'reports/index.html')

def report_suppliers_products(request):
    return render(request, 'reports/suppliers_products.html')

def report_customers_by_manufacturer(request):
    return render(request, 'reports/customers_by_manufacturer.html')

def report_warranty_repairs(request):
    return render(request, 'reports/warranty_repairs.html')

def report_sales_analytics(request):
    return render(request, 'reports/sales_analytics.html')

def report_components_by_price(request):
    return render(request, 'reports/components_by_price.html')

def report_suppliers_repair_frequency(request):
    return render(request, 'reports/suppliers_repair_frequency.html')

def report_custom_pc_components(request):
    return render(request, 'reports/custom_pc_components.html')

def report_supplier_deliveries(request):
    return render(request, 'reports/supplier_deliveries.html')

def report_contracts_period(request):
    return render(request, 'reports/contracts_period.html')

def report_supplier_by_contract(request):
    return render(request, 'reports/supplier_by_contract.html')