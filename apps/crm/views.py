# apps/crm/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponseForbidden
import json
from django.conf import settings
from datetime import datetime
from django.utils import timezone

# from apps.crm import models as crm_models  # якщо моделі у apps/crm/models.py
from apps.crm.models import Supplier, Sale, Supply, Employee, Repair, Contract
from apps.main.models import User, Product, ProductCategory, Delivery
from apps.api.serializers.main_serializers import ProductViewSerializer
from apps.crm.serializers.supplier_serializers import SupplierSerializer
from apps.crm.serializers.contract_serializer import ContractSerializer
from apps.crm.serializers.supply_serializer import SupplySerializer
from apps.crm.serializers.sale_serializer import SaleSerializer
from apps.crm.serializers.repair_serializer import RepairSerializer
from apps.crm.serializers.delivery_serializer import DeliverySerializer
import random


# Custom login_required decorator that works with JWT middleware
def login_required(view_func):
    """Custom login_required that works with JWT authentication"""
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request, 'user') or not request.user or not getattr(request.user, 'is_authenticated', False):
            login_url = getattr(settings, 'LOGIN_URL', '/auth/')
            messages.warning(request, 'Please log in to access this page.')
            return redirect(f"{login_url}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped


# допоміжна перевірка адмінства (як у тебе в токенах — role)
def admin_required(view_func):
    def _wrapped(request, *args, **kwargs):
        u = getattr(request, 'user', None)
        user_role = getattr(u, 'role', 'user') if u else 'user'
        if not u or not getattr(u, 'is_authenticated', False) or user_role not in ['operator', 'admin']:
            return HttpResponseForbidden("Access denied")
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@admin_required
def dashboard(request):
    # KPI
    suppliers_count = Supplier.objects().count()
    employees_count = Employee.objects().count()
    sales_count = Sale.objects().count()
    repairs_count = Repair.objects().filter(status__in=['received', 'diagnosed', 'repairing']).count()
    products_count = Product.objects().count()
    categories_count = ProductCategory.objects().count()
    users_count = User.objects().count()
    deliveries_count = Delivery.objects().count()

    # Latest items
    last_sales_sorted = Sale.objects().order_by('-created_at').limit(10).all()
    last_sales = [SaleSerializer(s).data for s in last_sales_sorted]

    last_repairs_sorted = Repair.objects().order_by('-created_at').limit(10).all()
    last_repairs = [RepairSerializer(r).data for r in last_repairs_sorted]

    recent_suppliers_sorted = Supplier.objects().order_by('-created_at').limit(8).all()
    recent_suppliers = [SupplierSerializer(s).data for s in recent_suppliers_sorted]
    
    recent_products_sorted = Product.objects().order_by('-created_at').limit(8).all()
    recent_products = [ProductViewSerializer(p).data for p in recent_products_sorted]

    context = {
        'suppliers_count': suppliers_count,
        'employees_count': employees_count,
        'sales_count': sales_count,
        'repairs_count': repairs_count,
        'products_count': products_count,
        'categories_count': categories_count,
        'users_count': users_count,
        'deliveries_count': deliveries_count,
        'last_sales': last_sales,
        'last_repairs': last_repairs,
        'recent_suppliers': recent_suppliers,
        'recent_products': recent_products,
    }
    return render(request, 'crm/dashboard.html', context)

@login_required
@admin_required
def analytics(request):
    from datetime import datetime, timedelta
    from django.utils import timezone
    
    now = timezone.now()
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Місячний прибуток (сума всіх продажів за поточний місяць)
    monthly_sales = Sale.objects().filter(
        sale_date__gte=current_month_start,
        status__in=['paid', 'pending']
    ).all()
    monthly_revenue = sum(float(sale.total_amount or 0) for sale in monthly_sales)
    
    # Кількість продажів за місяць
    monthly_sales_count = len(monthly_sales)
    
    # Нові клієнти за місяць (користувачі з role='user')
    new_customers = User.objects().filter(
        created_at__gte=current_month_start,
        role='user'
    ).count()
    
    # Закритих ремонтів (completed або returned)
    completed_repairs = Repair.objects().filter(
        status__in=['completed', 'returned']
    ).count()
    
    context = {
        'monthly_revenue': f"{monthly_revenue:,.2f}",
        'monthly_sales_count': monthly_sales_count,
        'new_customers': new_customers,
        'completed_repairs': completed_repairs,
    }
    
    return render(request, "crm/analytics.html", context)


# ---------- Suppliers ----------
@login_required
@admin_required
def suppliers_list(request):
    suppliers = Supplier.objects().order_by("-created_at").all()
    return render(request, "crm/suppliers_list.html", {"suppliers": suppliers})

@login_required
@admin_required
def suppliers_create(request):
    if request.method == 'POST':
        serializer = SupplierSerializer(data=request.POST)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Supplier created")
            return redirect("crm:suppliers_list")

        return render(request, "crm/supplier_form.html", {
            "action": "create",
            "errors": serializer.errors,
            "form": request.POST
        })

    return render(request, "crm/supplier_form.html", {"action": "create"})

@login_required
@admin_required
def suppliers_edit(request, pk):
    supplier = Supplier.find_by_id(pk)
    if not supplier:
        messages.error(request, "Supplier Not found")
        return redirect("crm:suppliers_list")

    if request.method == "POST":
        serializer = SupplierSerializer(supplier, data=request.POST)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Supplier updated")
            return redirect("crm:suppliers_list")

        return render(request, "crm/supplier_form.html", {
            "action": "edit",
            "supplier": supplier,
            "errors": serializer.errors,
            "form": request.POST
        })

    return render(request, "crm/supplier_form.html", {
        "action": "edit",
        "supplier": supplier
    })

@login_required
@admin_required
@api_view(['POST'])
def suppliers_delete(request, pk):
    supplier = Supplier.find_by_id(pk)
    if not supplier:
        return Response({"success": False}, status=404)
    supplier.delete()
    return Response({"success": True})

# categories = [ProductCategorySerializer(c).data for c in categories_sorted]

# ---------- Contracts ----------
@login_required
@admin_required
def contracts_list(request):
    contracts_sorted = Contract.objects().order_by('-created_at').all()
    contracts = [ContractSerializer(c).data for c in contracts_sorted]
    return render(request, 'crm/contracts_list.html', {'contracts': contracts})

@login_required
@admin_required
def contracts_create(request):
    if request.method == 'POST':
        data = request.POST.copy()

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        products = []
        total_amount = 0.0
        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if not pid:
                continue
            quantity = int(qty or 0)
            unit_price = float(price or 0)
            products.append({
                "product_id": pid,
                "quantity": quantity,
                "unit_price": unit_price,
            })
            total_amount += quantity * unit_price

        # Use calculated total_amount if not provided or is 0
        form_total = data.get("total_amount")
        if form_total:
            try:
                total_amount = float(form_total)
            except (ValueError, TypeError):
                pass  # Use calculated total_amount

        payload = {
            "supplier_id": data.get("supplier_id"),
            "total_amount": total_amount,
            "signing_date": data.get("signing_date") or None,
            "status": data.get("status") or "active",
            "notes": data.get("notes"),
            "products": products,
        }

        serializer = ContractSerializer(data=payload)

        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Contract created")
            return redirect("crm:contracts_list")

        STATUS_CHOICES = [
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ]
        suppliers = Supplier.objects().all()
        products_qs = Product.objects().all()

        return render(request, "crm/contract_form.html", {
            "action": "create",
            "errors": serializer.errors,
            "form": request.POST,
            "suppliers": suppliers,
            "products": products_qs,
            "STATUS_CHOICES": STATUS_CHOICES,
            "contract": None,
        })

    # GET як був
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    suppliers = Supplier.objects().all()
    products = Product.objects().all()
    context = {
        'suppliers': suppliers,
        'products': products,
        'STATUS_CHOICES': STATUS_CHOICES,
        'action': 'create',
        'contract': None,
    }
    return render(request, 'crm/contract_form.html', context)


@login_required
@admin_required
def contracts_edit(request, pk):
    contract = Contract.find_by_id(pk)
    if not contract:
        messages.error(request, 'Contract not found')
        return redirect('crm:contracts_list')

    if request.method == 'POST':
        # Get product data from form
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        products = []
        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if not pid:
                continue
            products.append({
                "product_id": pid,
                "quantity": int(qty or 0),
                "unit_price": float(price or 0),
            })

        # Update contract fields
        contract.number = request.POST.get('number', contract.number)
        contract.total_amount = float(request.POST.get('total_amount') or 0)
        contract.status = request.POST.get('status', contract.status)
        contract.notes = request.POST.get('notes', contract.notes)
        contract.products = products if products else contract.products
        
        # Auto recalc total if products changed
        if products:
            contract.total_amount = sum(
                item["unit_price"] * item["quantity"]
                for item in products
            )
        
        contract.updated_at = datetime.now()
        try:
            contract.save()
            messages.success(request, 'Contract updated successfully')
            return redirect('crm:contracts_list')
        except Exception as e:
            messages.error(request, f'Error updating contract: {e}')

    # Prepare context for form
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    suppliers = Supplier.objects().all()
    products = Product.objects().all()
    
    # Normalize contract products for template (convert dict/ObjectId to simple format)
    contract_products = []
    if contract and hasattr(contract, 'products') and contract.products:
        for item in contract.products:
            # Handle both dict and object formats
            if isinstance(item, dict):
                product_id = str(item.get('product_id', ''))
                quantity = item.get('quantity', 0) or 0
                unit_price = item.get('unit_price', 0) or 0
            else:
                product_id = str(getattr(item, 'product_id', ''))
                quantity = getattr(item, 'quantity', 0) or 0
                unit_price = getattr(item, 'unit_price', 0) or 0
            
            contract_products.append({
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price
            })
    
    return render(request, 'crm/contract_form.html', {
        'contract': contract,
        'suppliers': suppliers,
        'products': products,
        'STATUS_CHOICES': STATUS_CHOICES,
        'contract_products': contract_products,
        'action': 'edit'
    })

@login_required
@admin_required
@api_view(['POST'])
def contracts_delete(request, pk):
    contract = Contract.find_by_id(pk)
    if not contract:
        return Response({"success": False}, status=404)
    contract.delete()
    return Response({"success": True})


# ---------- Supplies ----------
@login_required
@admin_required
def supplies_list(request):
    supplies_sorted = Supply.objects().order_by('-created_at').all()
    supplies = [SupplySerializer(s).data for s in supplies_sorted]
    return render(request, 'crm/supplies_list.html', {'supplies': supplies})

@login_required
@admin_required
def supplies_create(request):
    if request.method == 'POST':
        contract_id = request.POST.get('contract_id')
        contract = Contract.find_by_id(contract_id)
        
        if not contract:
            messages.error(request, 'Contract not found')
            return redirect('crm:supplies_list')
        
        # Get products from contract
        contract_products = contract.products if hasattr(contract, 'products') and contract.products else []
        
        # Convert products to dict format if needed
        products_list = []
        total_cost = 0.0
        
        for product_item in contract_products:
            # Handle both dict and object formats
            if isinstance(product_item, dict):
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                unit_price = product_item.get('unit_price', 0) or 0
            else:
                product_id = getattr(product_item, 'product_id', None)
                quantity = getattr(product_item, 'quantity', 0) or 0
                unit_price = getattr(product_item, 'unit_price', 0) or 0
            
            if product_id:
                products_list.append({
                    'product_id': str(product_id) if hasattr(product_id, '__str__') else product_id,
                    'quantity': quantity,
                    'unit_price': unit_price
                })
                total_cost += float(quantity) * float(unit_price)
        
        # Parse delivery_date from form
        delivery_date_str = request.POST.get('delivery_date')
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
            except ValueError:
                delivery_date = datetime.now()
        else:
            delivery_date = datetime.now()
        
        data = {
            'contract_id': contract_id,
            'supplier_id': str(contract.supplier_id),  # Get supplier_id from contract
            'products': products_list,
            'total_cost': total_cost,
            'delivery_date': delivery_date,
            'status': request.POST.get('status') or 'ordered',
            'notes': request.POST.get('notes') or None,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
        
        Supply.create(**data)
        messages.success(request, 'Supply created successfully')
        return redirect('crm:supplies_list')
    
    # Filter contracts: only active and completed (not cancelled)
    contracts = Contract.objects().filter(status__in=['active']).all()
    suppliers = Supplier.objects().all()
    products = Product.objects().all()
    
    # Prepare contracts data with products for JavaScript
    contracts_data = []
    for contract in contracts:
        supplier = Supplier.find_by_id(contract.supplier_id) if contract.supplier_id else None
        contract_products = []
        contract_total = 0.0
        
        for product_item in (contract.products if hasattr(contract, 'products') and contract.products else []):
            if isinstance(product_item, dict):
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                unit_price = product_item.get('unit_price', 0) or 0
            else:
                product_id = getattr(product_item, 'product_id', None)
                quantity = getattr(product_item, 'quantity', 0) or 0
                unit_price = getattr(product_item, 'unit_price', 0) or 0
            
            if product_id:
                product = Product.find_by_id(product_id)
                contract_products.append({
                    'product_id': str(product_id),
                    'product_name': product.name if product else 'Unknown Product',
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': float(quantity) * float(unit_price)
                })
                contract_total += float(quantity) * float(unit_price)
        
        contracts_data.append({
            'id': str(contract.id),
            'number': contract.number,
            'supplier_id': str(contract.supplier_id) if contract.supplier_id else None,
            'supplier_name': supplier.name if supplier else 'Unknown Supplier',
            'products': contract_products,
            'total_amount': contract_total or (contract.total_amount if hasattr(contract, 'total_amount') else 0)
        })
    
    return render(request, 'crm/supply_form.html', {
        'contracts': contracts,
        'suppliers': suppliers,
        'products': products,
        'contracts_data': json.dumps(contracts_data)
    })

@login_required
@admin_required
def supplies_edit(request, pk):
    supply = Supply.find_by_id(pk)
    if not supply:
        messages.error(request, 'Supply not found')
        return redirect('crm:supplies_list')
    
    if request.method == 'POST':
        # Зберігаємо старий статус та received_date для перевірки зміни
        old_status = supply.status
        old_received_date = supply.received_date
        
        # Parse delivery_date from form
        delivery_date_str = request.POST.get('delivery_date')
        if delivery_date_str:
            try:
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
                supply.delivery_date = delivery_date
            except ValueError:
                pass  # Keep existing delivery_date
        
        # Parse received_date if provided
        received_date_str = request.POST.get('received_date')
        if received_date_str:
            try:
                received_date = datetime.strptime(received_date_str, '%Y-%m-%d')
                supply.received_date = received_date
            except ValueError:
                pass
        
        # Update supplier_id if changed
        supplier_id = request.POST.get('supplier_id')
        if supplier_id:
            supply.supplier_id = supplier_id
        
        # Оновлюємо статус
        new_status = request.POST.get('status', supply.status)
        supply.status = new_status
        
        # Якщо статус змінився на 'received', оновлюємо кількість продуктів на складі
        # АЛЕ тільки якщо received_date ще не було заповнене (захист від повторного оновлення)
        if new_status == 'received' and old_status != 'received' and not old_received_date:
            # Встановлюємо received_date якщо його немає
            if not supply.received_date:
                supply.received_date = datetime.now()
            
            # Оновлюємо кількість продуктів на складі
            if hasattr(supply, 'products') and supply.products:
                for product_item in supply.products:
                    # Обробляємо як dict, так і object формат
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                        quantity = product_item.get('quantity', 0) or 0
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                        quantity = getattr(product_item, 'quantity', 0) or 0
                    
                    if product_id:
                        try:
                            # Конвертуємо product_id в рядок якщо потрібно (find_by_id приймає рядок або ObjectId)
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                # Знаходимо продукт
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Додаємо кількість з поставки до наявної кількості
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    product.quantity_in_stock = current_quantity + int(quantity)
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            # Логуємо помилку, але продовжуємо обробку інших продуктів
                            print(f"Помилка при оновленні продукту {product_id}: {e}")
        
        supply.notes = request.POST.get('notes') or None
        supply.updated_at = datetime.now()
        supply.save()
        messages.success(request, 'Supply updated successfully')
        return redirect('crm:supplies_list')
    
    # Filter contracts: only active and completed (not cancelled)
    contracts = Contract.objects().filter(status__in=['active', 'completed']).all()
    suppliers = Supplier.objects().all()
    products = Product.objects().all()
    
    # Get contract data for selected contract
    contracts_data = []
    selected_contract = None
    if supply and supply.contract_id:
        selected_contract = Contract.find_by_id(supply.contract_id)
    
    for contract in contracts:
        supplier = Supplier.find_by_id(contract.supplier_id) if contract.supplier_id else None
        contract_products = []
        contract_total = 0.0
        
        for product_item in (contract.products if hasattr(contract, 'products') and contract.products else []):
            if isinstance(product_item, dict):
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                unit_price = product_item.get('unit_price', 0) or 0
            else:
                product_id = getattr(product_item, 'product_id', None)
                quantity = getattr(product_item, 'quantity', 0) or 0
                unit_price = getattr(product_item, 'unit_price', 0) or 0
            
            if product_id:
                product = Product.find_by_id(product_id)
                contract_products.append({
                    'product_id': str(product_id),
                    'product_name': product.name if product else 'Unknown Product',
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'subtotal': float(quantity) * float(unit_price)
                })
                contract_total += float(quantity) * float(unit_price)
        
        contracts_data.append({
            'id': str(contract.id),
            'number': contract.number,
            'supplier_id': str(contract.supplier_id) if contract.supplier_id else None,
            'supplier_name': supplier.name if supplier else 'Unknown Supplier',
            'products': contract_products,
            'total_amount': contract_total or (contract.total_amount if hasattr(contract, 'total_amount') else 0)
        })
    
    return render(request, 'crm/supply_form.html', {
        'supply': supply,
        'contracts': contracts,
        'suppliers': suppliers,
        'products': products,
        'contracts_data': json.dumps(contracts_data),
        'selected_contract': selected_contract
    })

@login_required
@admin_required
@api_view(['POST'])
def supplies_delete(request, pk):
    supply = Supply.find_by_id(pk)
    if not supply:
        return Response({"success": False}, status=404)
    supply.delete()
    return Response({"success": True})


# ---------- Employees ----------
@login_required
@admin_required
def employees_list(request):
    employees = Employee.objects().order_by('-created_at').all()
    return render(request, 'crm/employees_list.html', {'employees': employees})

@login_required
@admin_required
def employees_create(request):
    emp = Employee()

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        position = request.POST.get('position', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        salary = request.POST.get('salary', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Валідація
        errors = {}
        
        if not full_name or len(full_name) < 2:
            errors['full_name'] = 'Full name must be at least 2 characters'
        
        if not position:
            errors['position'] = 'Position is required'
        
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            import re
            if not re.match(email_pattern, email):
                errors['email'] = 'Please enter a valid email address'
            else:
                # Перевірка унікальності email
                existing_email = Employee.objects().filter(email=email).first()
                if existing_email:
                    errors['email'] = 'Employee with this email already exists'
        
        if phone:
            # Перевірка унікальності phone
            existing_phone = Employee.objects().filter(phone=phone).first()
            if existing_phone:
                errors['phone'] = 'Employee with this phone number already exists'
        
        if salary:
            try:
                salary_float = float(salary)
                if salary_float < 0:
                    errors['salary'] = 'Salary cannot be negative'
            except ValueError:
                errors['salary'] = 'Salary must be a valid number'
        
        if errors:
            return render(request, 'crm/employee_form.html', {
                'action': 'create',
                'employee': emp,
                'errors': errors,
                'form': request.POST
            })
        
        data = {
            'full_name': full_name,
            'position': position,
            'email': email or None,
            'phone': phone or None,
            'hire_date': datetime.now(),
            'salary': float(salary) if salary else None,
            'is_active': is_active,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        try:
            Employee.create(**data)
            messages.success(request, 'Employee created successfully')
            return redirect('crm:employees_list')
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
            return render(request, 'crm/employee_form.html', {
                'action': 'create',
                'employee': emp,
                'errors': {'general': str(e)},
                'form': request.POST
            })
    
    return render(request, 'crm/employee_form.html', {
        'action': 'create',
        'employee': emp,
        'errors': {}
    })

@login_required
@admin_required
def employees_edit(request, pk):
    emp = Employee.find_by_id(pk)
    if not emp:
        messages.error(request, 'Employee not found')
        return redirect('crm:employees_list')
    
    if request.method == 'POST':
        hire_date_str = request.POST.get('hire_date')
        if hire_date_str:
            try:
                emp.hire_date = datetime.fromisoformat(hire_date_str)
            except ValueError:
                pass
        
        full_name = request.POST.get('full_name', '').strip()
        position = request.POST.get('position', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        salary = request.POST.get('salary', '').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Валідація
        errors = {}
        
        if not full_name or len(full_name) < 2:
            errors['full_name'] = 'Full name must be at least 2 characters'
        
        if not position:
            errors['position'] = 'Position is required'
        
        if email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            import re
            if not re.match(email_pattern, email):
                errors['email'] = 'Please enter a valid email address'
            else:
                # Перевірка унікальності email (ігноруємо поточного працівника)
                existing_email = Employee.objects().filter(email=email).first()
                if existing_email and str(existing_email.id) != str(pk):
                    errors['email'] = 'Employee with this email already exists'
        
        if phone:
            # Перевірка унікальності phone (ігноруємо поточного працівника)
            existing_phone = Employee.objects().filter(phone=phone).first()
            if existing_phone and str(existing_phone.id) != str(pk):
                errors['phone'] = 'Employee with this phone number already exists'
        
        if salary:
            try:
                salary_float = float(salary)
                if salary_float < 0:
                    errors['salary'] = 'Salary cannot be negative'
            except ValueError:
                errors['salary'] = 'Salary must be a valid number'
        
        if errors:
            return render(request, 'crm/employee_form.html', {
                'action': 'edit',
                'employee': emp,
                'errors': errors,
                'form': request.POST
            })
        
        emp.full_name = full_name
        emp.position = position
        emp.email = email or None
        emp.phone = phone or None
        emp.salary = float(salary) if salary else None
        emp.is_active = is_active
        emp.updated_at = datetime.now()
        
        try:
            emp.save()
            messages.success(request, 'Employee updated successfully')
            return redirect('crm:employees_list')
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
            return render(request, 'crm/employee_form.html', {
                'action': 'edit',
                'employee': emp,
                'errors': {'general': str(e)},
                'form': request.POST
            })
    
    return render(request, 'crm/employee_form.html', {
        'action': 'edit',
        'employee': emp
    })

@login_required
@admin_required
@api_view(['POST'])
def employees_delete(request, pk):
    employee = Employee.find_by_id(pk)
    if not employee:
        return Response({"success": False}, status=404)
    employee.delete()
    return Response({"success": True})


# ---------- Sales ----------
@login_required
@admin_required
def sales_list(request):
    sales_sorted = Sale.objects().order_by('-created_at').all()
    sales = [SaleSerializer(s).data for s in sales_sorted]
    return render(request, 'crm/sales_list.html', {'sales': sales})

@login_required
@admin_required
def sales_create(request):
    if request.method == 'POST':
        # Parse products
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        
        products = []
        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if not pid:
                continue
            
            # Get product price if unit_price is not provided or is 0
            unit_price = float(price or 0)
            if unit_price == 0:
                product = Product.find_by_id(pid)
                if product:
                    unit_price = float(product.price or 0)
            
            products.append({
                "product_id": pid,
                "quantity": int(qty or 0),
                "unit_price": unit_price,
            })
        
        # Calculate total amount
        total_amount = sum((float(p['quantity']) * float(p['unit_price'])) for p in products)
        
        # Handle custom build
        custom_build_config = None
        if request.POST.get('has_custom_build') == 'on':
            custom_build_products = []
            cb_product_ids = request.POST.getlist('cb_product_id[]')
            cb_quantities = request.POST.getlist('cb_quantity[]')
            cb_prices = request.POST.getlist('cb_unit_price[]')
            
            for pid, qty, price in zip(cb_product_ids, cb_quantities, cb_prices):
                if not pid:
                    continue
                custom_build_products.append({
                    "product_id": pid,
                    "quantity": int(qty or 0),
                    "unit_price": float(price or 0),
                })
            
            if custom_build_products:
                custom_build_total_cost = sum((float(p['quantity']) * float(p['unit_price'])) for p in custom_build_products)
                
                # Create dict structure for CustomBuildConfig
                custom_build_dict = {
                    "name": request.POST.get('custom_build_name', 'Custom PC Build'),
                    "products": custom_build_products,
                    "total_cost": custom_build_total_cost,
                    "status": "ordered",
                    "notes": request.POST.get('custom_build_notes', '')
                }
                
                custom_build_config = {
                    "purchased": True,
                    "data": custom_build_dict,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                total_amount += custom_build_total_cost
        
        # Handle software service
        software_service_config = None
        if request.POST.get('has_software_service') == 'on':
            software_list = [s.strip() for s in request.POST.get('software_list', '').split(',') if s.strip()]
            software_cost = float(request.POST.get('software_cost', 0))
            software_date = datetime.fromisoformat(request.POST.get('software_date', datetime.now().isoformat()))
            
            # Create dict structure for SoftwareServiceConfig
            software_service_dict = {
                "description": request.POST.get('software_description', ''),
                "software_list": software_list,
                "date_scheduled": software_date,
                "cost": software_cost,
                "status": "scheduled"
            }
            
            software_service_config = {
                "purchased": True,
                "data": software_service_dict,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            total_amount += software_cost
        
        # Create sale
        sale_data = {
            'user_id': request.POST.get('user_id'),
            'employee_id': request.POST.get('employee_id'),
            'products': products,
            'total_amount': total_amount,
            'sale_date': datetime.fromisoformat(request.POST.get('sale_date', datetime.now().isoformat())),
            'status': request.POST.get('status') or 'paid',
            'payment_method': request.POST.get('payment_method') or 'cash',
            'warranty_end_date': datetime.fromisoformat(request.POST.get('warranty_end_date')) if request.POST.get('warranty_end_date') else None,
            'notes': request.POST.get('notes', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Add embedded fields only if they exist
        if custom_build_config:
            sale_data['custom_build_service'] = custom_build_config
        if software_service_config:
            sale_data['software_service'] = software_service_config
        
        # Створюємо продаж
        sale = Sale.create(**sale_data)
        
        # Віднімаємо кількість продуктів, які продалися
        if products:
            for product_item in products:
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                
                if product_id and quantity > 0:
                    try:
                        product_id_str = str(product_id) if product_id else None
                        if product_id_str:
                            product = Product.find_by_id(product_id_str)
                            if product:
                                current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                new_quantity = max(0, current_quantity - int(quantity))
                                product.quantity_in_stock = new_quantity
                                product.updated_at = datetime.now()
                                product.save()
                    except Exception as e:
                        # Логуємо помилку, але продовжуємо обробку інших продуктів
                        print(f"Помилка при оновленні продукту {product_id}: {e}")
        
        # Віднімаємо кількість продуктів, які використалися для збірки (custom build)
        if custom_build_config and custom_build_config.get('data') and custom_build_config['data'].get('products'):
            custom_build_products = custom_build_config['data']['products']
            for product_item in custom_build_products:
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                
                if product_id and quantity > 0:
                    try:
                        product_id_str = str(product_id) if product_id else None
                        if product_id_str:
                            product = Product.find_by_id(product_id_str)
                            if product:
                                current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                new_quantity = max(0, current_quantity - int(quantity))
                                product.quantity_in_stock = new_quantity
                                product.updated_at = datetime.now()
                                product.save()
                    except Exception as e:
                        # Логуємо помилку, але продовжуємо обробку інших продуктів
                        print(f"Помилка при оновленні продукту з custom build {product_id}: {e}")
        
        messages.success(request, 'Sale created successfully')
        return redirect('crm:sales_list')
    
    users = User.objects().all()
    employees = Employee.objects().all()
    products = Product.objects().filter(quantity_in_stock__gt=0).all()
    return render(request, 'crm/sale_form.html', {
        'users': users,
        'employees': employees,
        'products': products,
        'components': [p for p in products if p.category == 'component'],
        'action': 'create'
    })

@login_required
@admin_required
def sales_edit(request, pk):
    sale = Sale.find_by_id(pk)
    if not sale:
        messages.error(request, 'Sale not found')
        return redirect('crm:sales_list')
    
    if request.method == 'POST':
        # Зберігаємо старий статус для перевірки зміни
        old_status = sale.status
        
        # Update basic fields
        new_status = request.POST.get('status', sale.status)
        sale.status = new_status
        sale.payment_method = request.POST.get('payment_method', sale.payment_method)
        sale.notes = request.POST.get('notes', sale.notes)
        
        # Update products if provided
        product_ids = request.POST.getlist('product_id[]')
        if product_ids:
            quantities = request.POST.getlist('quantity[]')
            unit_prices = request.POST.getlist('unit_price[]')
            products = []
            for pid, qty, price in zip(product_ids, quantities, unit_prices):
                if not pid:
                    continue
                
                # Get product price if unit_price is not provided or is 0
                unit_price = float(price or 0)
                if unit_price == 0:
                    product = Product.find_by_id(pid)
                    if product:
                        unit_price = float(product.price or 0)
                
                products.append({
                    "product_id": pid,
                    "quantity": int(qty or 0),
                    "unit_price": unit_price,
                })
            sale.products = products
        
        # Recalculate total
        total_amount = sum((float(p['quantity']) * float(p['unit_price'])) for p in sale.products)
        
        # Handle custom build update if provided
        if request.POST.get('has_custom_build') == 'on':
            custom_build_products = []
            cb_product_ids = request.POST.getlist('cb_product_id[]')
            cb_quantities = request.POST.getlist('cb_quantity[]')
            cb_prices = request.POST.getlist('cb_unit_price[]')
            
            for pid, qty, price in zip(cb_product_ids, cb_quantities, cb_prices):
                if not pid:
                    continue
                
                # Get product price if unit_price is not provided or is 0
                unit_price = float(price or 0)
                if unit_price == 0:
                    product = Product.find_by_id(pid)
                    if product:
                        unit_price = float(product.price or 0)
                
                custom_build_products.append({
                    "product_id": pid,
                    "quantity": int(qty or 0),
                    "unit_price": unit_price,
                })
            
            if custom_build_products:
                custom_build_total_cost = sum((float(p['quantity']) * float(p['unit_price'])) for p in custom_build_products)
                
                custom_build_dict = {
                    "name": request.POST.get('custom_build_name', 'Custom PC Build'),
                    "products": custom_build_products,
                    "total_cost": custom_build_total_cost,
                    "status": "ordered",
                    "notes": request.POST.get('custom_build_notes', '')
                }
                
                # Отримати created_at з існуючого custom_build_service (якщо він є)
                existing_created_at = datetime.now()
                if sale.custom_build_service:
                    if isinstance(sale.custom_build_service, dict):
                        existing_created_at = sale.custom_build_service.get('created_at', datetime.now())
                    elif hasattr(sale.custom_build_service, 'created_at'):
                        existing_created_at = sale.custom_build_service.created_at or datetime.now()
                
                sale.custom_build_service = {
                    "purchased": True,
                    "data": custom_build_dict,
                    "created_at": existing_created_at,
                    "updated_at": datetime.now()
                }
                total_amount += custom_build_total_cost
        elif request.POST.get('remove_custom_build') == 'on':
            sale.custom_build_service = None
        
        # Handle software service update if provided
        if request.POST.get('has_software_service') == 'on':
            software_list = [s.strip() for s in request.POST.get('software_list', '').split(',') if s.strip()]
            software_cost = float(request.POST.get('software_cost', 0))
            software_date = datetime.fromisoformat(request.POST.get('software_date', datetime.now().isoformat()))
            
            software_service_dict = {
                "description": request.POST.get('software_description', ''),
                "software_list": software_list,
                "date_scheduled": software_date,
                "cost": software_cost,
                "status": "scheduled"
            }
            
            # Отримати created_at з існуючого software_service (якщо він є)
            existing_created_at = datetime.now()
            if sale.software_service:
                if isinstance(sale.software_service, dict):
                    existing_created_at = sale.software_service.get('created_at', datetime.now())
                elif hasattr(sale.software_service, 'created_at'):
                    existing_created_at = sale.software_service.created_at or datetime.now()
            
            sale.software_service = {
                "purchased": True,
                "data": software_service_dict,
                "created_at": existing_created_at,
                "updated_at": datetime.now()
            }
            total_amount += software_cost
        elif request.POST.get('remove_software_service') == 'on':
            sale.software_service = None
        
        sale.total_amount = total_amount
        sale.updated_at = datetime.now()
        
        # Обробка зміни статусу на 'cancelled' - повертаємо продукти на склад
        if new_status == 'cancelled' and old_status != 'cancelled':
            # Повертаємо кількість проданих продуктів на склад
            if hasattr(sale, 'products') and sale.products:
                for product_item in sale.products:
                    # Обробляємо як dict, так і object формат
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                        quantity = product_item.get('quantity', 0) or 0
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                        quantity = getattr(product_item, 'quantity', 0) or 0
                    
                    if product_id and quantity > 0:
                        try:
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Додаємо кількість назад на склад
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    product.quantity_in_stock = current_quantity + int(quantity)
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            print(f"Помилка при поверненні продукту {product_id} на склад: {e}")
            
            # Повертаємо кількість продуктів зі збірки на склад
            if hasattr(sale, 'custom_build_service') and sale.custom_build_service:
                custom_build_data = sale.custom_build_service
                # Обробляємо як dict, так і object формат
                if isinstance(custom_build_data, dict):
                    custom_build_products = custom_build_data.get('data', {}).get('products', [])
                elif hasattr(custom_build_data, 'data'):
                    custom_build_products = getattr(custom_build_data.data, 'products', []) if hasattr(custom_build_data.data, 'products') else []
                else:
                    custom_build_products = []
                
                for product_item in custom_build_products:
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                        quantity = product_item.get('quantity', 0) or 0
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                        quantity = getattr(product_item, 'quantity', 0) or 0
                    
                    if product_id and quantity > 0:
                        try:
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Додаємо кількість назад на склад
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    product.quantity_in_stock = current_quantity + int(quantity)
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            print(f"Помилка при поверненні продукту з custom build {product_id} на склад: {e}")
        
        # Обробка зміни статусу з 'cancelled' на інший - знову віднімаємо продукти
        elif old_status == 'cancelled' and new_status != 'cancelled':
            # Віднімаємо кількість проданих продуктів зі складу
            if hasattr(sale, 'products') and sale.products:
                for product_item in sale.products:
                    # Обробляємо як dict, так і object формат
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                        quantity = product_item.get('quantity', 0) or 0
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                        quantity = getattr(product_item, 'quantity', 0) or 0
                    
                    if product_id and quantity > 0:
                        try:
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    new_quantity = max(0, current_quantity - int(quantity))
                                    product.quantity_in_stock = new_quantity
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            print(f"Помилка при відніманні продукту {product_id} зі складу: {e}")
            
            # Віднімаємо кількість продуктів зі збірки зі складу
            if hasattr(sale, 'custom_build_service') and sale.custom_build_service:
                custom_build_data = sale.custom_build_service
                # Обробляємо як dict, так і object формат
                if isinstance(custom_build_data, dict):
                    custom_build_products = custom_build_data.get('data', {}).get('products', [])
                elif hasattr(custom_build_data, 'data'):
                    custom_build_products = getattr(custom_build_data.data, 'products', []) if hasattr(custom_build_data.data, 'products') else []
                else:
                    custom_build_products = []
                
                for product_item in custom_build_products:
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                        quantity = product_item.get('quantity', 0) or 0
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                        quantity = getattr(product_item, 'quantity', 0) or 0
                    
                    if product_id and quantity > 0:
                        try:
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    new_quantity = max(0, current_quantity - int(quantity))
                                    product.quantity_in_stock = new_quantity
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            print(f"Помилка при відніманні продукту з custom build {product_id} зі складу: {e}")
        
        sale.save()
        messages.success(request, 'Sale updated successfully')
        return redirect('crm:sales_list')
    
    users = User.objects().all()
    employees = Employee.objects().all()
    products = Product.objects().all()
    return render(request, 'crm/sale_form.html', {
        'sale': sale,
        'users': users,
        'employees': employees,
        'products': products,
        'components': [p for p in products if p.category == 'component'],
        'action': 'edit'
    })

@login_required
@admin_required
@api_view(['POST'])
def sales_delete(request, pk):
    sale = Sale.find_by_id(pk)
    if not sale:
        return Response({"success": False}, status=404)
    sale.delete()
    return Response({"success": True})


# ---------- Repairs ----------
@login_required
@admin_required
def repairs_list(request):
    repairs_sorted = Repair.objects().order_by('-created_at').all()
    repairs = [RepairSerializer(r).data for r in repairs_sorted]
    return render(request, 'crm/repairs_list.html', {'repairs': repairs})

@login_required
@admin_required
def repairs_create(request):
    if request.method == 'POST':
        # Get required fields
        user_id = request.POST.get('user_id', '').strip()
        employee_id = request.POST.get('employee_id', '').strip()
        description = request.POST.get('description', '').strip()
        repair_type = request.POST.get('repair_type', '').strip() or 'paid'
        status = request.POST.get('status', '').strip() or 'received'  # Use 'received' as default to match model
        
        # Validate required fields
        if not user_id:
            messages.error(request, 'Customer is required')
            users = User.objects().all()
            products = Product.objects().filter(quantity_in_stock__gt=0).all()
            employees = Employee.objects().all()
            return render(request, 'crm/repair_form.html', {
                'users': users,
                'products': products,
                'employees': employees,
                'form': request.POST
            })
        
        if not employee_id:
            messages.error(request, 'Employee is required')
            users = User.objects().all()
            products = Product.objects().filter(quantity_in_stock__gt=0).all()
            employees = Employee.objects().all()
            return render(request, 'crm/repair_form.html', {
                'users': users,
                'products': products,
                'employees': employees,
                'form': request.POST
            })
        
        if not description:
            messages.error(request, 'Description is required')
            users = User.objects().all()
            products = Product.objects().filter(quantity_in_stock__gt=0).all()
            employees = Employee.objects().all()
            return render(request, 'crm/repair_form.html', {
                'users': users,
                'products': products,
                'employees': employees,
                'form': request.POST
            })
        
        # Parse start_date from form or use current date
        start_date_str = request.POST.get('start_date')
        if start_date_str:
            try:
                # If it's just a date (YYYY-MM-DD), convert to datetime
                if len(start_date_str) == 10:  # Date only format
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                else:
                    start_date = datetime.fromisoformat(start_date_str)
            except (ValueError, TypeError):
                start_date = datetime.now()
        else:
            start_date = datetime.now()
        
        # Parse estimated_completion if provided
        estimated_completion = None
        estimated_completion_str = request.POST.get('estimated_completion')
        if estimated_completion_str:
            try:
                # If it's just a date (YYYY-MM-DD), convert to datetime
                if len(estimated_completion_str) == 10:  # Date only format
                    estimated_completion = datetime.strptime(estimated_completion_str, '%Y-%m-%d')
                else:
                    estimated_completion = datetime.fromisoformat(estimated_completion_str)
            except (ValueError, TypeError):
                pass
        
        # Get product_id - only if not empty
        product_id = request.POST.get('product_id', '').strip()
        if not product_id:
            product_id = None
        
        # Process products used
        used_product_ids = request.POST.getlist('used_product_id[]')
        used_quantities = request.POST.getlist('used_quantity[]')
        used_prices = request.POST.getlist('used_unit_price[]')
        
        products_used = []
        total_cost = 0
        
        for pid, qty, price in zip(used_product_ids, used_quantities, used_prices):
            if not pid:
                continue
            
            # Get product price if unit_price is not provided or is 0
            unit_price = float(price or 0)
            if unit_price == 0:
                product = Product.find_by_id(pid)
                if product:
                    unit_price = float(product.price or 0)
            
            products_used.append({
                "product_id": pid,
                "quantity": int(qty or 0),
                "unit_price": unit_price,
            })
            total_cost += float(qty or 0) * unit_price
        
        # Build data dictionary - ensure None values for empty strings
        data = {
            'user_id': user_id if user_id else None,
            'employee_id': employee_id if employee_id else None,
            'description': description if description else None,
            'repair_type': repair_type if repair_type else 'paid',
            'status': status if status else 'received',
            'cost': total_cost,
            'start_date': start_date,
            'products_used': products_used,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
        }
        
        # Add optional fields only if they have values
        if product_id:
            data['product_id'] = product_id
        
        if estimated_completion:
            data['estimated_completion'] = estimated_completion
        
        notes = request.POST.get('notes', '').strip()
        if notes:
            data['notes'] = notes
        
        # Debug: print all data before creating
        import sys
        print("=== REPAIR CREATE DEBUG ===", file=sys.stderr)
        for key, value in data.items():
            print(f"{key}: {value} (type: {type(value)})", file=sys.stderr)
        print("===========================", file=sys.stderr)
        
        # Validate all required fields are present and not empty
        required_fields = {
            'user_id': data.get('user_id'),
            'employee_id': data.get('employee_id'),
            'description': data.get('description'),
            'repair_type': data.get('repair_type'),
            'status': data.get('status'),
            'start_date': data.get('start_date'),
        }
        
        missing_fields = []
        for field_name, field_value in required_fields.items():
            if field_value is None or (isinstance(field_value, str) and field_value.strip() == ''):
                missing_fields.append(field_name)
        
        if missing_fields:
            messages.error(request, f'Missing required fields: {", ".join(missing_fields)}')
            users = User.objects().all()
            products = Product.objects().filter(quantity_in_stock__gt=0).all()
            employees = Employee.objects().all()
            return render(request, 'crm/repair_form.html', {
                'users': users,
                'products': products,
                'employees': employees,
                'form': request.POST
            })
        
        try:
            repair = Repair.create(**data)
            
            # Віднімаємо кількість використаних продуктів зі складу
            if products_used:
                for product_item in products_used:
                    product_id = product_item.get('product_id')
                    quantity = product_item.get('quantity', 0) or 0
                    
                    if product_id and quantity > 0:
                        try:
                            product_id_str = str(product_id) if product_id else None
                            if product_id_str:
                                product = Product.find_by_id(product_id_str)
                                if product:
                                    # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                    current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                    new_quantity = max(0, current_quantity - int(quantity))
                                    product.quantity_in_stock = new_quantity
                                    product.updated_at = datetime.now()
                                    product.save()
                        except Exception as e:
                            # Логуємо помилку, але продовжуємо обробку інших продуктів
                            print(f"Помилка при відніманні продукту {product_id} зі складу: {e}")
            
            messages.success(request, 'Repair created successfully')
            return redirect('crm:repairs_list')
        except ValueError as e:
            import traceback
            error_details = traceback.format_exc()
            print("=== REPAIR CREATE ERROR ===", file=sys.stderr)
            print(error_details, file=sys.stderr)
            print("===========================", file=sys.stderr)
            messages.error(request, f'Validation error: {str(e)}. Please check all required fields are filled.')
            users = User.objects().all()
            products = Product.objects().filter(quantity_in_stock__gt=0).all()
            employees = Employee.objects().all()
            return render(request, 'crm/repair_form.html', {
                'users': users,
                'products': products,
                'employees': employees,
                'form': request.POST
            })
    users = User.objects().all()
    products = Product.objects().filter(quantity_in_stock__gt=0).all()
    employees = Employee.objects().all()
    return render(request, 'crm/repair_form.html', {
        'users': users,
        'products': products,
        'employees': employees,
        'repair_products_used': []
    })

@login_required
@admin_required
def repairs_edit(request, pk):
    repair = Repair.find_by_id(pk)
    if not repair:
        messages.error(request, 'Ремонт не знайдено')
        return redirect('crm:repairs_list')
    if request.method == 'POST':
        # Зберігаємо старі використані продукти для відновлення кількості
        old_products_used = repair.products_used if hasattr(repair, 'products_used') and repair.products_used else []
        
        repair.description = request.POST.get('description')
        repair.status = request.POST.get('status')
        
        # Process products used
        used_product_ids = request.POST.getlist('used_product_id[]')
        used_quantities = request.POST.getlist('used_quantity[]')
        used_prices = request.POST.getlist('used_unit_price[]')
        
        products_used = []
        total_cost = 0.0
        
        for pid, qty, price in zip(used_product_ids, used_quantities, used_prices):
            if not pid:
                continue
            
            # Get product price if unit_price is not provided or is 0
            unit_price = float(price or 0)
            if unit_price == 0:
                product = Product.find_by_id(pid)
                if product:
                    unit_price = float(product.price or 0)
            
            products_used.append({
                "product_id": pid,
                "quantity": int(qty or 0),
                "unit_price": unit_price,
            })
            total_cost += float(qty or 0) * unit_price
        
        repair.products_used = products_used
        repair.cost = total_cost
        repair.notes = request.POST.get('notes')
        repair.updated_at = datetime.now()
        repair.save()
        
        # Повертаємо кількість старих продуктів на склад
        if old_products_used:
            for product_item in old_products_used:
                # Обробляємо як dict, так і object формат
                if isinstance(product_item, dict):
                    product_id = product_item.get('product_id')
                    quantity = product_item.get('quantity', 0) or 0
                else:
                    product_id = getattr(product_item, 'product_id', None)
                    quantity = getattr(product_item, 'quantity', 0) or 0
                
                if product_id and quantity > 0:
                    try:
                        product_id_str = str(product_id) if product_id else None
                        if product_id_str:
                            product = Product.find_by_id(product_id_str)
                            if product:
                                # Повертаємо кількість на склад
                                current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                product.quantity_in_stock = current_quantity + int(quantity)
                                product.updated_at = datetime.now()
                                product.save()
                    except Exception as e:
                        print(f"Помилка при поверненні продукту {product_id} на склад: {e}")
        
        # Віднімаємо кількість нових продуктів зі складу
        if products_used:
            for product_item in products_used:
                product_id = product_item.get('product_id')
                quantity = product_item.get('quantity', 0) or 0
                
                if product_id and quantity > 0:
                    try:
                        product_id_str = str(product_id) if product_id else None
                        if product_id_str:
                            product = Product.find_by_id(product_id_str)
                            if product:
                                # Віднімаємо кількість, але не дозволяємо від'ємні значення
                                current_quantity = getattr(product, 'quantity_in_stock', 0) or 0
                                new_quantity = max(0, current_quantity - int(quantity))
                                product.quantity_in_stock = new_quantity
                                product.updated_at = datetime.now()
                                product.save()
                    except Exception as e:
                        print(f"Помилка при відніманні продукту {product_id} зі складу: {e}")
        
        messages.success(request, 'Repair updated successfully')
        return redirect('crm:repairs_list')
    
    users = User.objects().all()
    products = Product.objects().all()
    employees = Employee.objects().all()
    
    # Normalize products_used for template rendering
    repair_products_used = []
    if repair.products_used:
        for item in repair.products_used:
            if isinstance(item, dict):
                repair_products_used.append(item)
            else:
                # If it's a model instance, convert to dict
                repair_products_used.append({
                    'product_id': getattr(item, 'product_id', ''),
                    'quantity': getattr(item, 'quantity', 0),
                    'unit_price': getattr(item, 'unit_price', 0)
                })
    
    return render(request, 'crm/repair_form.html', {
        'repair': repair,
        'repair_products_used': repair_products_used,
        'users': users,
        'products': products,
        'employees': employees
    })

@login_required
@admin_required
@api_view(['POST'])
def repairs_delete(request, pk):
    repair = Repair.find_by_id(pk)
    if not repair:
        return Response({"success": False}, status=404)
    repair.delete()
    return Response({"success": True})


# ---------- Deliveries ----------
@login_required
@admin_required
def deliveries_list(request):
    deliveries_sorted = Delivery.objects().order_by('-created_at').all()
    deliveries = [DeliverySerializer(d).data for d in deliveries_sorted]
    return render(request, 'crm/deliveries_list.html', {'deliveries': deliveries})

@login_required
@admin_required
def deliveries_create(request):
    # Get all sales with status 'paid' (оплачено), products, users for dropdowns
    sales_sorted = Sale.objects().filter(status='paid').order_by('-sale_date').all()
    sales = [SaleSerializer(s).data for s in sales_sorted]
    products_qs = Product.objects().all()
    users = User.objects().all()
    
    if request.method == 'POST':
        data = request.POST.copy()
        
        sale_id = data.get('sale_id')
        if not sale_id:
            messages.error(request, 'Sale is required')
            return render(request, 'crm/delivery_form.html', {
                'sales': sales,
                'products': products_qs,
                'users': users,
                'errors': {'sale_id': ['This field is required']}
            })
        
        # Get sale to extract user_id and products
        sale = Sale.find_by_id(sale_id)
        if not sale:
            messages.error(request, 'Sale not found')
            return render(request, 'crm/delivery_form.html', {
                'sales': sales,
                'products': products_qs,
                'users': users
            })
        
        # Get products from form or from sale
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        
        products = []
        if product_ids and len(product_ids) > 0 and product_ids[0]:
            # Products from form (if manually edited)
            for pid, qty, price in zip(product_ids, quantities, unit_prices):
                if not pid:
                    continue
                products.append({
                    "product_id": pid,
                    "quantity": int(qty or 0),
                    "unit_price": float(price or 0),
                })
        else:
            # Products from sale (default)
            if sale.products:
                for item in sale.products:
                    if isinstance(item, dict):
                        products.append({
                            "product_id": str(item.get('product_id', '')),
                            "quantity": item.get('quantity', 0) or 0,
                            "unit_price": item.get('unit_price', 0) or 0,
                        })
        
        # total_cost is delivery cost (manually entered), not order total
        total_cost = float(data.get("total_cost") or 0)
        
        # Parse delivery_date from form (datetime-local format: YYYY-MM-DDTHH:mm)
        delivery_date_str = request.POST.get('delivery_date')
        
        if delivery_date_str:
            try:
                # Parse datetime-local format: YYYY-MM-DDTHH:mm
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%dT%H:%M')
                # Ensure seconds and microseconds are 0
                delivery_date = delivery_date.replace(second=0, microsecond=0)
            except ValueError:
                # Fallback: try to parse as date only
                try:
                    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').replace(hour=9, minute=0, second=0, microsecond=0)
                except ValueError:
                    delivery_date = datetime.now().replace(second=0, microsecond=0)
        else:
            delivery_date = datetime.now().replace(second=0, microsecond=0)
        
        payload = {
            "sale_id": sale_id,
            "user_id": str(sale.user_id),  # Auto-filled from sale
            "delivery_address": request.POST.get('delivery_address') or '',
            "products": products,
            "total_cost": total_cost,  # Delivery cost (manual)
            "delivery_date": delivery_date,
            "status": request.POST.get('status') or "ordered",
            "notes": request.POST.get('notes'),
        }
        
        serializer = DeliverySerializer(data=payload)
        
        if serializer.is_valid():
            serializer.save()
            
            # Змінюємо статус продажу на 'pending' (відправлено)
            if sale:
                sale.status = 'pending'
                sale.updated_at = datetime.now()
                sale.save()
            
            messages.success(request, 'Delivery created successfully')
            return redirect('crm:deliveries_list')
        
        return render(request, 'crm/delivery_form.html', {
            'sales': sales,
            'products': products_qs,
            'users': users,
            'errors': serializer.errors,
            'form': request.POST
        })
    
    # GET request
    return render(request, 'crm/delivery_form.html', {
        'sales': sales,
        'products': products_qs,
        'users': users
    })

@login_required
@admin_required
def deliveries_edit(request, pk):
    delivery = Delivery.find_by_id(pk)
    if not delivery:
        messages.error(request, 'Delivery not found')
        return redirect('crm:deliveries_list')
    
    # Get all sales with status 'paid' (оплачено), products, users for dropdowns
    sales_sorted = Sale.objects().order_by('-sale_date').all()
    sales = [SaleSerializer(s).data for s in sales_sorted]
    products = Product.objects().all()
    users = User.objects().all()
    
    if request.method == 'POST':
        data = request.POST.copy()
        
        # Get products from form (if provided) or use existing products
        # In delivery form, products are read-only, so they may not be in POST
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        
        products = []
        if product_ids and len(product_ids) > 0 and product_ids[0]:
            # Products from form (if manually edited)
            for pid, qty, price in zip(product_ids, quantities, unit_prices):
                if not pid:
                    continue
                products.append({
                    "product_id": pid,
                    "quantity": int(qty or 0),
                    "unit_price": float(price or 0),
                })
        else:
            # Products are read-only in delivery form, so use existing products
            if delivery.products:
                for item in delivery.products:
                    if isinstance(item, dict):
                        product_id = item.get('product_id', '')
                        products.append({
                            "product_id": str(product_id) if product_id else '',
                            "quantity": item.get('quantity', 0) or 0,
                            "unit_price": item.get('unit_price', 0) or 0,
                        })
                    else:
                        # Handle object format
                        product_id = getattr(item, 'product_id', None)
                        products.append({
                            "product_id": str(product_id) if product_id else '',
                            "quantity": getattr(item, 'quantity', 0) or 0,
                            "unit_price": getattr(item, 'unit_price', 0) or 0,
                        })
        
        # total_cost is delivery cost (manually entered), not order total
        total_cost = float(data.get("total_cost") or 0)
        
        # Parse delivery_date from form (datetime-local format: YYYY-MM-DDTHH:mm)
        delivery_date_str = data.get("delivery_date")
        
        if delivery_date_str:
            try:
                # Parse datetime-local format: YYYY-MM-DDTHH:mm
                delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%dT%H:%M')
                # Ensure seconds and microseconds are 0
                delivery_date = delivery_date.replace(second=0, microsecond=0)
            except ValueError:
                # Fallback: try to parse as date only
                try:
                    delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d')
                    # Use time from existing delivery_date if available, otherwise default to 9:00
                    if delivery.delivery_date:
                        delivery_date = delivery_date.replace(
                            hour=delivery.delivery_date.hour,
                            minute=delivery.delivery_date.minute,
                            second=0,
                            microsecond=0
                        )
                    else:
                        delivery_date = delivery_date.replace(hour=9, minute=0, second=0, microsecond=0)
                except ValueError:
                    delivery_date = delivery.delivery_date
        else:
            delivery_date = delivery.delivery_date
        
        # Parse received_date from form (optional)
        received_date = None
        received_date_str = data.get("received_date")
        if received_date_str:
            try:
                # Parse date and set time to midnight (00:00:00)
                received_date = datetime.strptime(received_date_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0, microsecond=0)
            except ValueError:
                received_date = delivery.received_date if hasattr(delivery, 'received_date') else None
        
        payload = {
            "sale_id": str(delivery.sale_id),
            "user_id": str(delivery.user_id),
            "delivery_address": data.get("delivery_address", delivery.delivery_address if hasattr(delivery, 'delivery_address') else ""),
            "products": products,
            "total_cost": total_cost,  # Delivery cost (manual)
            "delivery_date": delivery_date,
            "received_date": received_date,
            "status": data.get("status") or delivery.status,
            "notes": data.get("notes") or delivery.notes,
        }
        
        serializer = DeliverySerializer(instance=delivery, data=payload)
        
        if serializer.is_valid():
            serializer.save()
            messages.success(request, 'Delivery updated successfully')
            return redirect('crm:deliveries_list')
        
        # Normalize delivery products for template
        delivery_products = []
        if delivery.products:
            for item in delivery.products:
                if isinstance(item, dict):
                    delivery_products.append({
                        'product_id': str(item.get('product_id', '')),
                        'quantity': item.get('quantity', 0) or 0,
                        'unit_price': item.get('unit_price', 0) or 0,
                    })
        
        return render(request, 'crm/delivery_form.html', {
            'delivery': delivery,
            'delivery_products': delivery_products,
            'sales': sales,
            'products': products,
            'users': users,
            'errors': serializer.errors
        })
    
    # GET request
    # Normalize delivery products for template
    delivery_products = []
    if delivery.products:
        for item in delivery.products:
            if isinstance(item, dict):
                delivery_products.append({
                    "product": Product.find_by_id(item["product_id"]).to_dict() if Product.find_by_id(item["product_id"]) else None,
                    'product_id': str(item.get('product_id', '')),
                    'quantity': item.get('quantity', 0) or 0,
                    'unit_price': item.get('unit_price', 0) or 0,
                })
    
    # Convert delivery.sale_id to string for template comparison
    delivery_sale_id_str = str(delivery.sale_id) if delivery.sale_id else None
    
    return render(request, 'crm/delivery_form.html', {
        'delivery': delivery,
        'delivery_sale_id_str': delivery_sale_id_str,  # String version for comparison
        'delivery_products': delivery_products,
        'sales': sales,
        'products': products,
        'users': users
    })

@login_required
@admin_required
@api_view(['POST'])
def deliveries_delete(request, pk):
    delivery = Delivery.find_by_id(pk)
    if not delivery:
        return Response({"success": False}, status=404)
    delivery.delete()
    return Response({"success": True})


# ---------- Users (Admin and Operator) ----------
@login_required
def users_list(request):
    """Список користувачів (для адмінів та операторів - read-only для операторів)"""
    # Перевірка, що користувач є адміном або оператором
    user_role = getattr(request.user, 'role', 'user') if request.user else 'user'
    if user_role not in ['admin', 'operator']:
        return HttpResponseForbidden("Access denied. Admin or operator role required.")
    
    # Отримуємо всіх користувачів
    users = list(User.objects().all())
    
    # Визначаємо пріоритет ролі для сортування (user=0, operator=1, admin=2)
    def get_role_priority(role):
        role_priorities = {'user': 0, 'operator': 1, 'admin': 2}
        return role_priorities.get(role, 3)
    
    # Сортуємо: спочатку по ролі (user, operator, admin), потім по даті створення (новіші перші)
    def sort_key(user):
        role = getattr(user, 'role', 'user')
        role_priority = get_role_priority(role)
        created_at = getattr(user, 'created_at', None)
        # Якщо created_at є datetime об'єктом, використовуємо timestamp, інакше 0
        if created_at and isinstance(created_at, datetime):
            timestamp = created_at.timestamp()
        else:
            timestamp = 0
        return (role_priority, -timestamp)  # -timestamp для сортування від новіших до старіших
    
    users.sort(key=sort_key)
    
    return render(request, 'crm/users_list.html', {
        'users': users,
        'can_edit': user_role == 'admin'  # Тільки адмін може редагувати
    })


@login_required
def users_create(request):
    """Створення користувача (тільки для адмінів)"""
    # Перевірка, що користувач є адміном
    user_role = getattr(request.user, 'role', 'user') if request.user else 'user'
    if user_role != 'admin':
        return HttpResponseForbidden("Access denied. Admin role required.")
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        role = request.POST.get('role', 'user').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Валідація
        errors = {}
        
        if not username or len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
        elif User.objects().filter(username=username).first():
            errors['username'] = 'Username already exists'
        
        if not email or '@' not in email:
            errors['email'] = 'Valid email is required'
        elif User.objects().filter(email=email).first():
            errors['email'] = 'Email already exists'
        
        if not password or len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters'
        elif password != password_confirm:
            errors['password_confirm'] = 'Passwords do not match'
        
        # Адмін може призначати тільки 'user' та 'operator', не 'admin'
        if role not in ['user', 'operator']:
            errors['role'] = 'Admin can only assign "user" or "operator" roles'
        
        if errors:
            return render(request, 'crm/user_form.html', {
                'action': 'create',
                'errors': errors,
                'form': {
                    'username': username,
                    'email': email,
                    'role': role,
                    'is_active': 'on' if is_active else ''
                },
                'role_choices': [('user', 'User'), ('operator', 'Operator')]
            })
        
        # Створюємо користувача
        try:
            user = User(
                username=username,
                email=email,
                role=role,
                is_active=is_active,
                created_at=datetime.now()
            )
            user.set_password(password)
            user.save()
            
            messages.success(request, f'User "{username}" created successfully')
            return redirect('crm:users_list')
        except Exception as e:
            import traceback
            error_msg = str(e)
            print(f"Error creating user: {error_msg}")
            print(traceback.format_exc())
            messages.error(request, f'Error creating user: {error_msg}')
            return render(request, 'crm/user_form.html', {
                'action': 'create',
                'errors': {'general': error_msg},
                'form': {
                    'username': username,
                    'email': email,
                    'role': role,
                    'is_active': 'on' if is_active else ''
                },
                'role_choices': [('user', 'User'), ('operator', 'Operator')]
            })
    
    return render(request, 'crm/user_form.html', {
        'action': 'create',
        'errors': {},
        'form': {},
        'role_choices': [('user', 'User'), ('operator', 'Operator')]
    })


@login_required
def users_edit(request, pk):
    """Редагування користувача (тільки для адмінів)"""
    # Перевірка, що користувач є адміном
    user_role = getattr(request.user, 'role', 'user') if request.user else 'user'
    if user_role != 'admin':
        return HttpResponseForbidden("Access denied. Admin role required.")
    
    user = User.find_by_id(pk)
    if not user:
        messages.error(request, 'User not found')
        return redirect('crm:users_list')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        role = request.POST.get('role', 'user').strip()
        is_active = request.POST.get('is_active') == 'on'
        
        # Валідація
        errors = {}
        
        if not username or len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters'
        elif username != user.username and User.objects().filter(username=username).first():
            errors['username'] = 'Username already exists'
        
        if not email or '@' not in email:
            errors['email'] = 'Valid email is required'
        elif email != user.email and User.objects().filter(email=email).first():
            errors['email'] = 'Email already exists'
        
        # Пароль не обов'язковий при редагуванні
        if password:
            if len(password) < 6:
                errors['password'] = 'Password must be at least 6 characters'
            elif password != password_confirm:
                errors['password_confirm'] = 'Passwords do not match'
        
        # Адмін може призначати тільки 'user' та 'operator', не 'admin'
        # Але не може змінити роль існуючого адміна на іншу
        if user.role == 'admin' and role != 'admin':
            errors['role'] = 'Cannot change admin role'
        elif role not in ['user', 'operator']:
            errors['role'] = 'Admin can only assign "user" or "operator" roles'
        
        if errors:
            return render(request, 'crm/user_form.html', {
                'action': 'edit',
                'user': user,
                'errors': errors,
                'form': request.POST,
                'role_choices': [('user', 'User'), ('operator', 'Operator')]
            })
        
        # Оновлюємо користувача
        try:
            user.username = username
            user.email = email
            user.role = role
            user.is_active = is_active
            
            # Оновлюємо пароль тільки якщо він вказаний
            if password:
                user.set_password(password)
            
            user.save()
            
            messages.success(request, f'User "{username}" updated successfully')
            return redirect('crm:users_list')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')
            return render(request, 'crm/user_form.html', {
                'action': 'edit',
                'user': user,
                'errors': {'general': str(e)},
                'form': request.POST,
                'role_choices': [('user', 'User'), ('operator', 'Operator')]
            })
    
    return render(request, 'crm/user_form.html', {
        'action': 'edit',
        'user': user,
        'role_choices': [('user', 'User'), ('operator', 'Operator')]
    })


@login_required
@api_view(['POST'])
def users_delete(request, pk):
    """Видалення користувача (тільки для адмінів)"""
    # Перевірка, що користувач є адміном
    user_role = getattr(request.user, 'role', 'user') if request.user else 'user'
    if user_role != 'admin':
        return Response({"success": False, "message": "Access denied. Admin role required."}, status=403)

    user = User.find_by_id(pk)
    if not user:
        return Response({"success": False, "message": "User not found"}, status=404)
    
    # Не можна видалити самого себе
    if str(user.id) == str(request.user.id):
        return Response({"success": False, "message": "You cannot delete your own account"}, status=400)
    
    # Не можна видалити іншого адміна
    if user.role == 'admin':
        return Response({"success": False, "message": "Cannot delete admin user"}, status=400)
    
    try:
        username = user.username
        user.delete()
        return Response({"success": True, "message": f'User "{username}" deleted successfully'})
    except Exception as e:
        return Response({"success": False, "message": f'Error deleting user: {str(e)}'}, status=500)

# ---------- Product Categories ----------
@login_required
@admin_required
def product_categories_list(request):
    categories = ProductCategory.objects().order_by('-created_at').all()
    return render(request, 'crm/product_categories_list.html', {'categories': categories})

@login_required
@admin_required
def product_categories_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        
        if not name or not slug or not image_url:
            messages.error(request, 'Name, slug, and image URL are required')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_category_form.html', {
                'action': 'create',
                'form': request.POST,
                'categories': categories
            })
        
        # Валідація унікальності
        errors = {}
        
        existing_name = ProductCategory.objects().filter(name=name).first()
        if existing_name:
            errors['name'] = 'Category with this name already exists'
        
        existing_slug = ProductCategory.objects().filter(slug=slug).first()
        if existing_slug:
            errors['slug'] = 'Category with this slug already exists'
        
        existing_image_url = ProductCategory.objects().filter(image_url=image_url).first()
        if existing_image_url:
            errors['image_url'] = 'Category with this image URL already exists'
        
        if errors:
            return render(request, 'crm/product_category_form.html', {
                'action': 'create',
                'form': request.POST,
                'errors': errors
            })
        
        category = ProductCategory.create(
            name=name,
            slug=slug,
            description=description,
            image_url=image_url,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        messages.success(request, 'Product category created successfully')
        return redirect('crm:product_categories_list')
    
    return render(request, 'crm/product_category_form.html', {'action': 'create'})

@login_required
@admin_required
def product_categories_edit(request, pk):
    category = ProductCategory.find_by_id(pk)
    if not category:
        messages.error(request, 'Product category not found')
        return redirect('crm:product_categories_list')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        slug = request.POST.get('slug', '').strip()
        description = request.POST.get('description', '').strip()
        image_url = request.POST.get('image_url', '').strip()
        
        if not name or not slug or not image_url:
            messages.error(request, 'Name, slug, and image URL are required')
            return render(request, 'crm/product_category_form.html', {
                'action': 'edit',
                'category': category,
                'form': request.POST
            })
        
        # Валідація унікальності
        errors = {}
        
        existing_name = ProductCategory.objects().filter(name=name).first()
        if existing_name and str(existing_name.id) != str(pk):
            errors['name'] = 'Category with this name already exists'
        
        existing_slug = ProductCategory.objects().filter(slug=slug).first()
        if existing_slug and str(existing_slug.id) != str(pk):
            errors['slug'] = 'Category with this slug already exists'
        
        existing_image_url = ProductCategory.objects().filter(image_url=image_url).first()
        if existing_image_url and str(existing_image_url.id) != str(pk):
            errors['image_url'] = 'Category with this image URL already exists'
        
        if errors:
            return render(request, 'crm/product_category_form.html', {
                'action': 'edit',
                'category': category,
                'form': request.POST,
                'errors': errors
            })
        
        category.name = name
        category.slug = slug
        category.description = description
        category.image_url = image_url
        category.updated_at = datetime.now()
        category.save()
        
        messages.success(request, 'Product category updated successfully')
        return redirect('crm:product_categories_list')
    
    return render(request, 'crm/product_category_form.html', {
        'action': 'edit',
        'category': category
    })

@login_required
@admin_required
@api_view(['POST'])
def product_categories_delete(request, pk):
    category = ProductCategory.find_by_id(pk)
    if not category:
        return Response({"success": False, "message": "Product category not found"}, status=404)
    
    category.delete()
    return Response({"success": True, "message": "Product category deleted successfully"})


# ---------- Products ----------
@login_required
@admin_required
def products_list(request):
    products = Product.objects().order_by('-created_at').all()
    categories = ProductCategory.objects().all()
    return render(request, 'crm/products_list.html', {
        'products': products,
        'categories': categories
    })

@login_required
@admin_required
def products_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        product_type = request.POST.get('product_type', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        price = request.POST.get('price', '0')
        quantity_in_stock = request.POST.get('quantity_in_stock', '0')
        warranty_months = request.POST.get('warranty_months', '12')
        image_url = request.POST.get('image_url', '').strip()
        
        if not name or not category or not product_type or not manufacturer or not image_url:
            messages.error(request, 'Required fields: name, category, product_type, manufacturer, image_url')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'create',
                'categories': categories,
                'form': request.POST,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        try:
            price = float(price)
            quantity_in_stock = int(quantity_in_stock)
            warranty_months = int(warranty_months)
        except ValueError:
            messages.error(request, 'Invalid numeric values')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'create',
                'categories': categories,
                'form': request.POST,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        # Валідація унікальності
        errors = {}
        
        existing_name = Product.objects().filter(name=name).first()
        if existing_name:
            errors['name'] = 'Product with this name already exists'
        
        existing_image_url = Product.objects().filter(image_url=image_url).first()
        if existing_image_url:
            errors['image_url'] = 'Product with this image URL already exists'
        
        if errors:
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'create',
                'categories': categories,
                'form': request.POST,
                'errors': errors,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        # Process specifications
        spec_names = request.POST.getlist('spec_name[]')
        spec_slugs = request.POST.getlist('spec_slug[]')
        spec_values = request.POST.getlist('spec_value[]')
        
        specifications = []
        for spec_name, spec_slug, spec_value in zip(spec_names, spec_slugs, spec_values):
            if spec_name and spec_slug and spec_value:
                specifications.append({
                    'name': spec_name.strip(),
                    'slug': spec_slug.strip(),
                    'value': spec_value.strip()
                })
        
        try:
            product = Product.create(
                name=name,
                description=description,
                category=category,
                product_type=product_type,
                manufacturer=manufacturer,
                price=price,
                quantity_in_stock=quantity_in_stock,
                warranty_months=warranty_months,
                image_url=image_url,
                specifications=specifications,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            messages.success(request, 'Product created successfully')
            return redirect('crm:products_list')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'create',
                'categories': categories,
                'form': request.POST,
                'errors': {'general': str(e)},
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
    
    categories = ProductCategory.objects().all()
    return render(request, 'crm/product_form.html', {
        'action': 'create',
        'categories': categories,
        'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
    })

@login_required
@admin_required
def products_edit(request, pk):
    product = Product.find_by_id(pk)
    if not product:
        messages.error(request, 'Product not found')
        return redirect('crm:products_list')
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', '').strip()
        product_type = request.POST.get('product_type', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        price = request.POST.get('price', '0')
        quantity_in_stock = request.POST.get('quantity_in_stock', '0')
        warranty_months = request.POST.get('warranty_months', '12')
        image_url = request.POST.get('image_url', '').strip()
        
        if not name or not category or not product_type or not manufacturer or not image_url:
            messages.error(request, 'Required fields: name, category, product_type, manufacturer, image_url')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'edit',
                'product': product,
                'categories': categories,
                'form': request.POST,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        try:
            price = float(price)
            quantity_in_stock = int(quantity_in_stock)
            warranty_months = int(warranty_months)
        except ValueError:
            messages.error(request, 'Invalid numeric values')
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'edit',
                'product': product,
                'categories': categories,
                'form': request.POST,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        # Валідація унікальності
        errors = {}
        
        existing_name = Product.objects().filter(name=name).first()
        if existing_name and str(existing_name.id) != str(pk):
            errors['name'] = 'Product with this name already exists'
        
        existing_image_url = Product.objects().filter(image_url=image_url).first()
        if existing_image_url and str(existing_image_url.id) != str(pk):
            errors['image_url'] = 'Product with this image URL already exists'
        
        if errors:
            categories = ProductCategory.objects().all()
            return render(request, 'crm/product_form.html', {
                'action': 'edit',
                'product': product,
                'categories': categories,
                'form': request.POST,
                'errors': errors,
                'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
            })
        
        # Process specifications
        spec_names = request.POST.getlist('spec_name[]')
        spec_slugs = request.POST.getlist('spec_slug[]')
        spec_values = request.POST.getlist('spec_value[]')
        
        specifications = []
        for spec_name, spec_slug, spec_value in zip(spec_names, spec_slugs, spec_values):
            if spec_name and spec_slug and spec_value:
                specifications.append({
                    'name': spec_name.strip(),
                    'slug': spec_slug.strip(),
                    'value': spec_value.strip()
                })
        
        product.name = name
        product.description = description
        product.category = category
        product.product_type = product_type
        product.manufacturer = manufacturer
        product.price = price
        product.quantity_in_stock = quantity_in_stock
        product.warranty_months = warranty_months
        product.image_url = image_url
        product.specifications = specifications
        product.updated_at = datetime.now()
        product.save()
        
        messages.success(request, 'Product updated successfully')
        return redirect('crm:products_list')
    
    categories = ProductCategory.objects().all()
    
    # Normalize specifications for template rendering
    normalized_specs = []
    if product.specifications:
        for spec in product.specifications:
            if isinstance(spec, dict):
                normalized_specs.append(spec)
            else:
                # If it's a model instance, convert to dict
                normalized_specs.append({
                    'name': getattr(spec, 'name', ''),
                    'slug': getattr(spec, 'slug', ''),
                    'value': getattr(spec, 'value', '')
                })
    
    # Create a copy of product with normalized specifications
    product.specifications = normalized_specs
    
    return render(request, 'crm/product_form.html', {
        'action': 'edit',
        'product': product,
        'categories': categories,
        'PRODUCT_TYPE_CHOICES': Product.PRODUCT_TYPE_CHOICES
    })

@login_required
@admin_required
@api_view(['POST'])
def products_delete(request, pk):
    product = Product.find_by_id(pk)
    if not product:
        return Response({"success": False, "message": "Product not found"}, status=404)
    
    product.delete()
    return Response({"success": True, "message": "Product deleted successfully"})
