# apps/crm/queries_views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import datetime, timedelta
from collections import defaultdict

from apps.crm.models import Supplier, Contract, Supply, Sale, Repair, Employee
from apps.crm.serializers.contract_serializer import ContractSerializer
from apps.crm.serializers.sale_serializer import SaleSerializer
from apps.main.models import Product, User, CustomBuildConfig

# Import admin_required from views
from apps.crm.views import admin_required


def get_product_item_field(product_item, field_name, default=None):
    """Helper function to safely get field from product_item (can be dict or model instance)"""
    if isinstance(product_item, dict):
        return product_item.get(field_name, default)
    elif hasattr(product_item, field_name):
        return getattr(product_item, field_name, default)
    return default


@login_required
@admin_required
def queries_index(request):
    """Index page for queries"""
    return render(request, 'crm/queries_index.html')


# ==================== QUERY 1 ====================
@login_required
@admin_required
def query1_suppliers_with_products(request):
    """Query 1: Suppliers and their products"""
    suppliers = Supplier.objects().all()
    result = []
    
    for supplier in suppliers:
        contracts = Contract.objects().filter(supplier_id=supplier.id).all()
        products = []
        seen_products = set()
        
        for contract in contracts:
            if not contract.products:
                continue
            for product_item in contract.products:
                product_id = get_product_item_field(product_item, 'product_id')
                product_id_str = str(product_id) if product_id else None
                if not product_id_str or product_id_str in seen_products:
                    continue
                seen_products.add(product_id_str)
                
                product = Product.find_by_id(product_id)
                if product:
                    quantity = get_product_item_field(product_item, 'quantity', 0) or 0
                    unit_price = get_product_item_field(product_item, 'unit_price', 0) or 0
                    products.append({
                        'product': product,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'subtotal': round(float(quantity) * float(unit_price), 2)
                    })
        
        result.append({
            'supplier': supplier,
            'products': products,
            'total_products': len(products)
        })
    
    return render(request, 'crm/queries/query1_suppliers_products.html', {
        'results': result
    })


@login_required
@admin_required
def query1_components_multiple_suppliers(request):
    """Query 1b: Components supplied by 2+ suppliers"""
    product_suppliers = defaultdict(set)
    
    contracts = Contract.objects().all()
    for contract in contracts:
        if not contract.products:
            continue
        for product_item in contract.products:
            product_id = get_product_item_field(product_item, 'product_id')
            product_id = str(product_id) if product_id else None
            supplier_id = str(contract.supplier_id) if contract.supplier_id else None
            if product_id and supplier_id:
                product_suppliers[product_id].add(supplier_id)
    
    result = []
    component_types = [choice[0] for choice in Product.COMPONENT_CHOICES]
    
    for product_id, supplier_ids in product_suppliers.items():
        if len(supplier_ids) >= 2:
            product = Product.find_by_id(product_id)
            if product and product.product_type in component_types:
                suppliers_info = []
                for supplier_id in supplier_ids:
                    supplier = Supplier.find_by_id(supplier_id)
                    if supplier:
                        suppliers_info.append(supplier)
                
                result.append({
                    'product': product,
                    'suppliers': suppliers_info,
                    'suppliers_count': len(supplier_ids)
                })
    
    return render(request, 'crm/queries/query1_components_multiple.html', {
        'results': result
    })


# ==================== QUERY 2 ====================
@login_required
@admin_required
def query2_customers_by_manufacturer(request):
    """Query 2: Customers who bought products from specified manufacturer"""
    manufacturer = request.GET.get('manufacturer', '').strip()
    
    if not manufacturer:
        return render(request, 'crm/queries/query2_customers_manufacturer.html', {
            'results': [],
            'manufacturer': '',
            'error': 'Please specify manufacturer parameter'
        })
    
    products = Product.objects().filter(manufacturer__icontains=manufacturer).all()
    product_ids = [str(p.id) for p in products]
    
    if not product_ids:
        return render(request, 'crm/queries/query2_customers_manufacturer.html', {
            'results': [],
            'manufacturer': manufacturer,
            'error': f'No products found for manufacturer: {manufacturer}'
        })
    
    sales = Sale.objects().all()
    customer_ids = set()
    customer_sales = defaultdict(list)
    
    for sale in sales:
        if not sale.products:
            continue
        for product_item in sale.products:
            product_id = get_product_item_field(product_item, 'product_id')
            if product_id and str(product_id) in product_ids:
                customer_ids.add(sale.user_id)
                product = Product.find_by_id(product_id)
                customer_sales[sale.user_id].append({
                    'sale': sale,
                    'product': product,
                    'product_name': product.name if product else 'Unknown'
                })
    
    result = []
    for user_id in customer_ids:
        user = User.find_by_id(user_id)
        if user:
            result.append({
                'customer': user,
                'purchases': customer_sales[user_id],
                'total_purchases': len(customer_sales[user_id])
            })
    
    return render(request, 'crm/queries/query2_customers_manufacturer.html', {
        'results': result,
        'manufacturer': manufacturer
    })


# ==================== QUERY 3 ====================
@login_required
@admin_required
def query3_warranty_repairs_returned(request):
    """Query 3a: Products returned for warranty repair"""
    repairs = Repair.objects().filter(
        repair_type='warranty',
        status='returned'
    ).all()
    
    result = []
    for repair in repairs:
        product = Product.find_by_id(repair.product_id) if repair.product_id else None
        user = User.find_by_id(repair.user_id) if repair.user_id else None
        
        result.append({
            'repair': repair,
            'product': product,
            'customer': user
        })
    
    return render(request, 'crm/queries/query3_warranty_returned.html', {
        'results': result
    })


@login_required
@admin_required
def query3_warranty_repairs_completed(request):
    """Query 3b: Products completed warranty repair"""
    repairs = Repair.objects().filter(
        repair_type='warranty',
        status='completed'
    ).all()
    
    result = []
    for repair in repairs:
        product = Product.find_by_id(repair.product_id) if repair.product_id else None
        user = User.find_by_id(repair.user_id) if repair.user_id else None
        
        result.append({
            'repair': repair,
            'product': product,
            'customer': user
        })
    
    return render(request, 'crm/queries/query3_warranty_completed.html', {
        'results': result
    })


@login_required
@admin_required
def query3_warranty_repairs_in_progress(request):
    """Query 3c: Warranty repairs in progress"""
    repairs = Repair.objects().filter(
        repair_type='warranty',
        status__in=['received', 'diagnosed', 'repairing']
    ).all()
    
    result = []
    for repair in repairs:
        product = Product.find_by_id(repair.product_id) if repair.product_id else None
        user = User.find_by_id(repair.user_id) if repair.user_id else None
        employee = Employee.find_by_id(repair.employee_id) if repair.employee_id else None
        
        result.append({
            'repair': repair,
            'product': product,
            'customer': user,
            'employee': employee
        })
    
    return render(request, 'crm/queries/query3_warranty_in_progress.html', {
        'results': result
    })


# ==================== QUERY 4 ====================
@login_required
@admin_required
def query4_max_revenue_by_month(request):
    """Query 4a: Max revenue by month"""
    month_str = request.GET.get('month', '').strip()
    
    if not month_str:
        now = datetime.now()
        month_str = now.strftime('%Y-%m')
    
    try:
        year, month = map(int, month_str.split('-'))
        if not (1 <= month <= 12):
            raise ValueError('Month must be between 1 and 12')
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1)
        else:
            month_end = datetime(year, month + 1, 1)
    except (ValueError, IndexError) as e:
        return render(request, 'crm/queries/query4_max_revenue.html', {
            'error': f'Invalid month format. Use YYYY-MM. Error: {str(e)}',
            'month': month_str
        })
    
    sales = Sale.objects().filter(
        sale_date__gte=month_start,
        sale_date__lt=month_end
    ).all()
    
    max_revenue = 0
    max_sale = None
    
    for sale in sales:
        if sale.total_amount and sale.total_amount > max_revenue:
            max_revenue = sale.total_amount
            max_sale = sale
    
    return render(request, 'crm/queries/query4_max_revenue.html', {
        'month': month_str,
        'max_revenue': max_revenue,
        'max_sale': max_sale
    })


@login_required
@admin_required
def query4_revenue_by_product_type_last_week(request):
    """Query 4b: Revenue by product type for last week"""
    now = datetime.now()
    week_ago = now - timedelta(days=7)
    
    sales = Sale.objects().filter(
        sale_date__gte=week_ago,
        sale_date__lte=now
    ).all()
    
    revenue_by_type = defaultdict(float)
    
    for sale in sales:
        if not sale.products:
            continue
        for product_item in sale.products:
            product_id = get_product_item_field(product_item, 'product_id')
            product = Product.find_by_id(product_id) if product_id else None
            if product:
                product_type = product.product_type
                unit_price = get_product_item_field(product_item, 'unit_price', 0) or 0
                quantity = get_product_item_field(product_item, 'quantity', 0) or 0
                revenue = unit_price * quantity
                revenue_by_type[product_type] += revenue
    
    result = [
        {
            'product_type': product_type,
            'revenue': revenue
        }
        for product_type, revenue in sorted(revenue_by_type.items(), key=lambda x: x[1], reverse=True)
    ]
    
    return render(request, 'crm/queries/query4_revenue_by_type.html', {
        'results': result,
        'period_start': week_ago,
        'period_end': now,
        'total_revenue': sum(revenue_by_type.values())
    })


@login_required
@admin_required
def query4_sales_by_employee(request):
    """Query 4c: Sales per employee"""
    sales = Sale.objects().all()
    
    employee_sales = defaultdict(lambda: {
        'total_products': 0,
        'total_amount': 0,
        'sales_count': 0
    })
    
    for sale in sales:
        if not sale.employee_id:
            continue
        
        employee = Employee.find_by_id(sale.employee_id)
        if not employee:
            continue
        
        employee_id = str(employee.id)
        employee_sales[employee_id]['sales_count'] += 1
        employee_sales[employee_id]['total_amount'] += sale.total_amount or 0
        
        if sale.products:
            for product_item in sale.products:
                quantity = get_product_item_field(product_item, 'quantity', 0) or 0
                employee_sales[employee_id]['total_products'] += quantity
    
    result = []
    for employee_id, stats in employee_sales.items():
        employee = Employee.find_by_id(employee_id)
        if employee:
            result.append({
                'employee': employee,
                'statistics': stats
            })
    
    result.sort(key=lambda x: x['statistics']['total_products'], reverse=True)
    
    return render(request, 'crm/queries/query4_sales_by_employee.html', {
        'results': result
    })


# ==================== QUERY 5 ====================
@login_required
@admin_required
def query5_components_by_price(request):
    """Query 5: Components with price <= max_price"""
    try:
        max_price = float(request.GET.get('max_price', 0))
    except ValueError:
        max_price = 0
    
    if max_price <= 0:
        return render(request, 'crm/queries/query5_components_price.html', {
            'results': [],
            'max_price': 0,
            'error': 'Please specify max_price parameter (must be > 0)'
        })
    
    component_types = [choice[0] for choice in Product.COMPONENT_CHOICES]
    components = Product.objects().filter(
        product_type__in=component_types
    ).filter(
        price__lte=max_price
    ).order_by('price').all()
    
    return render(request, 'crm/queries/query5_components_price.html', {
        'results': components,
        'max_price': max_price
    })


# ==================== QUERY 6 ====================
@login_required
@admin_required
def query6_suppliers_by_repair_frequency(request):
    """Query 6: Suppliers whose products most frequently need repair"""
    repairs = Repair.objects().all()
    
    product_repair_count = defaultdict(int)
    for repair in repairs:
        if repair.product_id:
            product_repair_count[str(repair.product_id)] += 1
    
    supplier_repair_count = defaultdict(int)
    supplier_products = defaultdict(set)
    
    contracts = Contract.objects().all()
    for contract in contracts:
        if not contract.products:
            continue
        supplier_id = str(contract.supplier_id)
        for product_item in contract.products:
            product_id = get_product_item_field(product_item, 'product_id')
            product_id = str(product_id) if product_id else None
            if product_id:
                supplier_products[supplier_id].add(product_id)
                if product_id in product_repair_count:
                    supplier_repair_count[supplier_id] += product_repair_count[product_id]
    
    result = []
    for supplier_id, repair_count in sorted(supplier_repair_count.items(), key=lambda x: x[1], reverse=True):
        supplier = Supplier.find_by_id(supplier_id)
        if supplier:
            result.append({
                'supplier': supplier,
                'repairs_count': repair_count,
                'products_count': len(supplier_products[supplier_id])
            })
    
    return render(request, 'crm/queries/query6_suppliers_repairs.html', {
        'results': result
    })


# ==================== QUERY 7 ====================
@login_required
@admin_required
def query7_custom_build_components(request):
    """Query 7: Custom build components for customer"""
    user_id = request.GET.get('user_id')
    sale_id = request.GET.get('sale_id')
    
    if not user_id and not sale_id:
        return render(request, 'crm/queries/query7_custom_build.html', {
            'error': 'Please specify user_id or sale_id parameter'
        })
    
    sale_obj = None
    if sale_id:
        sale_obj = Sale.find_by_id(sale_id)
    elif user_id:
        sales = Sale.objects().filter(user_id=user_id).order_by('-sale_date').all()
        for s in sales:
            # Check if custom_build_service exists and is purchased (handle both dict and object)
            cbs = s.custom_build_service
            if cbs:
                purchased = False
                if isinstance(cbs, dict):
                    purchased = cbs.get('purchased', False)
                elif hasattr(cbs, 'purchased'):
                    purchased = cbs.purchased
                
                if purchased:
                    sale_obj = s
                    break
    
    if not sale_obj or not sale_obj.custom_build_service:
        return render(request, 'crm/queries/query7_custom_build.html', {
            'error': 'No sale with custom build found'
        })
    
    # Handle both dict and object formats
    custom_build_config = sale_obj.custom_build_service
    purchased = False
    if isinstance(custom_build_config, dict):
        purchased = custom_build_config.get('purchased', False)
        custom_build = custom_build_config.get('data', {})
    elif hasattr(custom_build_config, 'purchased'):
        purchased = custom_build_config.purchased
        custom_build = custom_build_config.data if hasattr(custom_build_config, 'data') else None
    else:
        custom_build = None
    
    if not purchased:
        return render(request, 'crm/queries/query7_custom_build.html', {
            'error': 'Custom build was not purchased'
        })
    
    if not custom_build:
        return render(request, 'crm/queries/query7_custom_build.html', {
            'error': 'Custom build data not found'
        })
    
    # Handle both dict and object formats for custom_build
    if isinstance(custom_build, dict):
        products = custom_build.get('products', [])
    elif hasattr(custom_build, 'products'):
        products = custom_build.products
    else:
        products = []
    
    if not products:
        return render(request, 'crm/queries/query7_custom_build.html', {
            'error': 'Custom build contains no products'
        })
    
    components = []
    for product_item in products:
        product_id = get_product_item_field(product_item, 'product_id')
        product = Product.find_by_id(product_id) if product_id else None
        if product:
            quantity = get_product_item_field(product_item, 'quantity', 0) or 0
            unit_price = get_product_item_field(product_item, 'unit_price', 0) or 0
            components.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'total_price': quantity * unit_price
            })
    
    # Serialize sale for template
    sale_data = SaleSerializer(sale_obj).data
    user = User.find_by_id(sale_obj.user_id) if sale_obj.user_id else None
    employee = Employee.find_by_id(sale_obj.employee_id) if sale_obj.employee_id else None
    
    # Get custom build name and other info
    if isinstance(custom_build, dict):
        custom_build_name = custom_build.get('name', 'Custom Build')
        custom_build_total_cost = custom_build.get('total_cost', 0)
        custom_build_status = custom_build.get('status', 'N/A')
        custom_build_notes = custom_build.get('notes', '')
    else:
        custom_build_name = getattr(custom_build, 'name', 'Custom Build')
        custom_build_total_cost = getattr(custom_build, 'total_cost', 0)
        custom_build_status = getattr(custom_build, 'status', 'N/A')
        custom_build_notes = getattr(custom_build, 'notes', '')
    
    return render(request, 'crm/queries/query7_custom_build.html', {
        'sale': sale_data,
        'customer': user,
        'employee': employee,
        'custom_build': {
            'name': custom_build_name,
            'total_cost': custom_build_total_cost,
            'status': custom_build_status,
            'notes': custom_build_notes
        },
        'components': components,
    })


# ==================== QUERY 8 ====================
@login_required
@admin_required
def query8_product_supplies_by_period(request):
    """Query 8: Product supplies by period"""
    product_id = request.GET.get('product_id')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    if not product_id:
        return render(request, 'crm/queries/query8_product_supplies.html', {
            'error': 'Please specify product_id parameter'
        })
    
    product = Product.find_by_id(product_id)
    if not product:
        return render(request, 'crm/queries/query8_product_supplies.html', {
            'error': 'Product not found'
        })
    
    try:
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime(2000, 1, 1)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.now()
    except (ValueError, AttributeError) as e:
        return render(request, 'crm/queries/query8_product_supplies.html', {
            'error': f'Invalid date format. Use format: YYYY-MM-DD. Error: {str(e)}',
            'product': product
        })
    
    supplies = Supply.objects().filter(
        delivery_date__gte=start_date,
        delivery_date__lte=end_date
    ).all()
    
    total_quantity = 0
    supplies_info = []
    
    for supply in supplies:
        if not supply.products:
            continue
        for product_item in supply.products:
            item_product_id = get_product_item_field(product_item, 'product_id')
            if item_product_id and str(item_product_id) == str(product_id):
                quantity = get_product_item_field(product_item, 'quantity', 0) or 0
                total_quantity += quantity
                
                supplier = Supplier.find_by_id(supply.supplier_id) if supply.supplier_id else None
                contract = Contract.find_by_id(supply.contract_id) if supply.contract_id else None
                
                supplies_info.append({
                    'supply': supply,
                    'supplier': supplier,
                    'contract': contract,
                    'quantity': quantity,
                    'unit_price': get_product_item_field(product_item, 'unit_price', 0) or 0
                })
    
    return render(request, 'crm/queries/query8_product_supplies.html', {
        'product': product,
        'period_start': start_date,
        'period_end': end_date,
        'total_quantity': total_quantity,
        'supplies': supplies_info
    })


# ==================== QUERY 9 ====================
@login_required
@admin_required
def query9_contracts_by_period(request):
    """Query 9a: Contracts by period"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    try:
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            except ValueError:
                start_date = datetime.fromisoformat(start_date_str)
        else:
            start_date = datetime(2000, 1, 1)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                # Set to end of day
                end_date = end_date.replace(hour=23, minute=59, second=59)
            except ValueError:
                end_date = datetime.fromisoformat(end_date_str)
        else:
            end_date = datetime.now()
    except (ValueError, AttributeError) as e:
        return render(request, 'crm/queries/query9_contracts_period.html', {
            'error': f'Invalid date format. Use format: YYYY-MM-DD. Error: {str(e)}'
        })
    
    contracts_sorted = Contract.objects().filter(
        signing_date__gte=start_date,
        signing_date__lte=end_date
    ).order_by('-signing_date').all()
    
    result = []
    for contract_obj in contracts_sorted:
        supplier = Supplier.find_by_id(contract_obj.supplier_id) if contract_obj.supplier_id else None
        # Serialize contract for template
        contract_data = ContractSerializer(contract_obj).data
        result.append({
            'contract': contract_data,
            'supplier': supplier
        })
    
    return render(request, 'crm/queries/query9_contracts_period.html', {
        'results': result,
        'period_start': start_date,
        'period_end': end_date
    })


@login_required
@admin_required
def query9_contracts_count_by_supplier(request):
    """Query 9b: Contract count by supplier"""
    contracts = Contract.objects().all()
    
    supplier_contracts = defaultdict(lambda: {
        'count': 0,
        'total_amount': 0,
        'contracts': []
    })
    
    for contract in contracts:
        supplier_id = str(contract.supplier_id) if contract.supplier_id else None
        if supplier_id:
            supplier_contracts[supplier_id]['count'] += 1
            supplier_contracts[supplier_id]['total_amount'] += contract.total_amount or 0
            supplier_contracts[supplier_id]['contracts'].append(contract)
    
    result = []
    for supplier_id, stats in supplier_contracts.items():
        supplier = Supplier.find_by_id(supplier_id)
        if supplier:
            # Serialize contracts for template
            contracts_data = [ContractSerializer(c).data for c in stats['contracts']]
            result.append({
                'supplier': supplier,
                'contracts_count': stats['count'],
                'total_amount': stats['total_amount'],
                'contracts': contracts_data
            })
    
    result.sort(key=lambda x: x['contracts_count'], reverse=True)
    
    return render(request, 'crm/queries/query9_contracts_count.html', {
        'results': result
    })


# ==================== QUERY 10 ====================
@login_required
@admin_required
def query10_supplier_by_contract_number(request):
    """Query 10: Supplier by contract number"""
    contract_number = request.GET.get('contract_number', '').strip()
    
    if not contract_number:
        return render(request, 'crm/queries/query10_supplier_contract.html', {
            'error': 'Please specify contract_number parameter'
        })
    
    contract = Contract.objects().filter(number=contract_number).first()
    
    if not contract:
        return render(request, 'crm/queries/query10_supplier_contract.html', {
            'error': f'Contract with number {contract_number} not found'
        })
    
    supplier = Supplier.find_by_id(contract.supplier_id) if contract.supplier_id else None
    
    if not supplier:
        return render(request, 'crm/queries/query10_supplier_contract.html', {
            'error': 'Supplier not found'
        })
    
    products_info = []
    if contract.products:
        for product_item in contract.products:
            product_id = get_product_item_field(product_item, 'product_id')
            product = Product.find_by_id(product_id) if product_id else None
            if product:
                products_info.append({
                    'product': product,
                    'quantity': get_product_item_field(product_item, 'quantity', 0) or 0,
                    'unit_price': get_product_item_field(product_item, 'unit_price', 0) or 0,
                    'subtotal': round(float(get_product_item_field(product_item, 'quantity', 0) or 0) * float(get_product_item_field(product_item, 'unit_price', 0) or 0), 2)
                })
    
    # Serialize contract for template
    contract_data = ContractSerializer(contract).data
    
    return render(request, 'crm/queries/query10_supplier_contract.html', {
        'contract': contract_data,
        'supplier': supplier,
        'products': products_info
    })

