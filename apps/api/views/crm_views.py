# apps/api/crm_views.py
import secrets

from bson import ObjectId
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from apps.customers.models import Customer
from apps.suppliers.models import Supplier
from apps.products.models import Product

# Тестові дані (замініть на реальні запити до MongoDB через MongoEngine)

# Постачальники
def api_suppliers_list(request):
    if request.method == 'GET':
        try:
            suppliers = Supplier.objects.order_by('name')
            suppliers_data = [s.to_json_dict() for s in suppliers]
            return JsonResponse({'suppliers': suppliers_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Невірний метод запиту'}, status=405)


def api_supplier_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            supplier = Supplier(
                name=data.get('name'),
                contact_person=data.get('contact_person'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address')
            )
            supplier.save()
            return JsonResponse({'status': 'success', 'message': 'Постачальника успішно додано!', 'redirect_url': '/suppliers/'}, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Помилка збереження: {e}'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Невірний метод запиту'}, status=405)


def api_supplier_detail(request, supplier_id):
    try:
        supplier = Supplier.objects.get(id=supplier_id)
    except Supplier.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Постачальника не знайдено'}, status=404)

    if request.method == 'GET':
        # Тут можна додати логіку для отримання пов'язаних даних, наприклад, договорів
        return JsonResponse({'supplier': supplier.to_json_dict()})

    if request.method == 'DELETE':
        try:
            supplier.delete()
            return JsonResponse({'status': 'success', 'message': 'Постачальника успішно видалено'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Помилка видалення: {e}'}, status=500)

    return JsonResponse({'status': 'error', 'message': f'Метод {request.method} не підтримується'}, status=405)


# Клієнти
def api_customers_list(request):
    # Замість mock-даних, отримуємо реальних клієнтів з бази даних
    try:
        customers = Customer.objects.order_by('-created_at')  # Сортуємо за датою створення
        # Перетворюємо об'єкти MongoEngine в список словників для JSON
        customers_data = [
            {
                # Явно перетворюємо ObjectId на рядок для надійності
                'id': str(customer.id),
                'name': customer.name,
                'surname': customer.surname,
                'phone': customer.phone,
                'email': customer.email,
                # Форматуємо дату в ISO 8601, щоб JS міг її легко розпарсити
                'created_at': customer.created_at.isoformat()
            } for customer in customers
        ]
        return JsonResponse({'customers': customers_data})
    except Exception as e:
        # Логування помилки буде корисним для дебагу
        print(f"Error fetching customers: {e}")
        return JsonResponse({'status': 'error', 'message': 'Помилка отримання даних клієнтів'}, status=500)

def api_customer_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Тут буде логіка збереження даних з форми в MongoDB
            # Наприклад, ви можете викликати функцію з вашого db_connector
            print("Отримано дані для нового клієнта:", data)

            # Створюємо новий об'єкт Customer
            customer = Customer(
                name=data.get('name'),
                surname=data.get('surname'),
                phone=data.get('phone'),
                email=data.get('email'),
                address=data.get('address')
            )
            customer.save()

            # Повертаємо успішну відповідь для AJAX-форми
            return JsonResponse({
                'status': 'success',
                'message': 'Клієнта успішно додано!',
                'redirect_url': '/customers/' # URL для перенаправлення після успішного збереження
            }, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Некоректний формат JSON'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Дозволено тільки POST-запити'}, status=405)

def api_customer_detail(request, customer_id):
    try:
        customer = Customer.objects.get(id=customer_id)
    except Customer.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Клієнта не знайдено'}, status=404)

    if request.method == 'GET':
        customer_data = {
            'id': str(customer.id),
            'name': customer.name,
            'surname': customer.surname,
            'phone': customer.phone,
            'email': customer.email,
            'address': customer.address,
            'created_at': customer.created_at.isoformat(),
        }
        return JsonResponse({'customer': customer_data})

    if request.method == 'DELETE':
        try:
            customer.delete()
            return JsonResponse({'status': 'success', 'message': 'Клієнта успішно видалено'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Помилка видалення: {e}'}, status=500)

    return JsonResponse({'status': 'error', 'message': f'Метод {request.method} не підтримується'}, status=405)


# Товари
def api_products_list(request):
    if request.method == 'GET':
        try:
            products = Product.objects.order_by('-created_at')
            products_data = [p.to_json_dict() for p in products]
            return JsonResponse({'products': products_data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Невірний метод запиту'}, status=405)


def api_product_add(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            product = Product(
                name=data.get('name'),
                category=data.get('category'),
                manufacturer=data.get('manufacturer'),
                model=data.get('model'),
                price=float(data.get('price', 0)),
                warranty_months=int(data.get('warranty_months', 12)),
                quantity_in_stock=int(data.get('quantity_in_stock', 0)),
                min_stock_level=int(data.get('min_stock_level', 1)),
                product_type=data.get('product_type', 'component')
            )
            product.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Товар успішно додано!',
                'redirect_url': '/products/'
            }, status=201)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Помилка збереження: {e}'}, status=400)


def api_product_detail(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Товар не знайдено'}, status=404)

    if request.method == 'GET':
        return JsonResponse({'product': product.to_json_dict()})

    if request.method == 'DELETE':
        try:
            product.delete()
            return JsonResponse({'status': 'success', 'message': 'Товар успішно видалено'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Помилка видалення: {e}'}, status=500)

    return JsonResponse({'status': 'error', 'message': f'Метод {request.method} не підтримується'}, status=405)


def api_categories_list(request):
    categories = [
        {'id': '674f1a2b8d4c5e123456789a', 'name': 'Процесори', 'products_count': 15},
        {'id': '674f1a2b8d4c5e123456789b', 'name': 'Відеокарти', 'products_count': 12},
        {'id': '674f1a2b8d4c5e123456789c', 'name': 'Материнські плати', 'products_count': 20},
        {'id': '674f1a2b8d4c5e123456789d', 'name': 'Оперативна пам\'ять', 'products_count': 18},
        {'id': '674f1a2b8d4c5e123456789e', 'name': 'SSD накопичувачі', 'products_count': 25},
        {'id': '674f1a2b8d4c5e123456789f', 'name': 'Блоки живлення', 'products_count': 10},
        {'id': '674f1a2b8d4c5e12345678a0', 'name': 'Ноутбуки', 'products_count': 8},
        {'id': '674f1a2b8d4c5e12345678a1', 'name': 'Периферія', 'products_count': 30}
    ]
    return JsonResponse({'categories': categories})


# Договори
def api_contracts_list(request):
    contracts_data = [
        {
            'id': '674f1a2b8d4c5e12345678a2',
            'number': 'DOG-2024-001',
            'supplier': 'ТехноТрейд',
            'date_signed': '2024-12-01',
            'delivery_date': '2024-12-15',
            'total_amount': 250000.00,
            'status': 'completed',
            'products_count': 5
        },
        {
            'id': '674f1a2b8d4c5e12345678a3',
            'number': 'DOG-2024-002',
            'supplier': 'КомпАльянс',
            'date_signed': '2024-12-10',
            'delivery_date': '2024-12-25',
            'total_amount': 180000.00,
            'status': 'active',
            'products_count': 3
        }
    ]
    return JsonResponse({'contracts': contracts_data})


def api_contract_detail(request, contract_id):
    contract = {
        'id': contract_id,
        'number': 'DOG-2024-001',
        'supplier': 'ТехноТрейд',
        'date_signed': '2024-12-01',
        'delivery_date': '2024-12-15',
        'total_amount': 250000.00,
        'status': 'completed',
        'products': [
            {'name': 'Intel Core i7-13700K', 'quantity': 10, 'unit_price': 15000.00},
            {'name': 'ASUS ROG Strix B550-F', 'quantity': 15, 'unit_price': 8000.00}
        ]
    }
    return JsonResponse({'contract': contract})


# Продажі
def api_sales_list(request):
    sales_data = [
        {
            'id': '674f1a2b8d4c5e12345678a4',
            'customer': 'Іван Іваненко',
            'employee': 'Олексій Мельник',
            'sale_date': '2024-12-20',
            'total_amount': 25000.00,
            'payment_method': 'card',
            'status': 'completed',
            'items_count': 2
        },
        {
            'id': '674f1a2b8d4c5e12345678a5',
            'customer': 'Марія Петрівна',
            'employee': 'Світлана Коваль',
            'sale_date': '2024-12-19',
            'total_amount': 35000.00,
            'payment_method': 'cash',
            'status': 'completed',
            'items_count': 3
        }
    ]
    return JsonResponse({'sales': sales_data})


def api_sale_detail(request, sale_id):
    sale = {
        'id': sale_id,
        'customer': 'Іван Іваненко',
        'employee': 'Олексій Мельник',
        'sale_date': '2024-12-20',
        'total_amount': 25000.00,
        'payment_method': 'card',
        'status': 'completed',
        'items': [
            {'product': 'Intel Core i7-13700K', 'quantity': 1, 'unit_price': 15000.00, 'total_price': 15000.00},
            {'product': 'Kingston FURY 16GB DDR4', 'quantity': 2, 'unit_price': 5000.00, 'total_price': 10000.00}
        ]
    }
    return JsonResponse({'sale': sale})


# Ремонти
def api_repairs_list(request):
    repairs_data = [
        {
            'id': '674f1a2b8d4c5e12345678a6',
            'customer': 'Олександр Сидоренко',
            'product': 'NVIDIA RTX 4070',
            'description': 'Не запускається, чорний екран',
            'is_warranty': True,
            'date_received': '2024-12-18',
            'status': 'repairing',
            'cost': 0.00
        },
        {
            'id': '674f1a2b8d4c5e12345678a7',
            'customer': 'Марія Петрівна',
            'product': 'Logitech MX Master 3',
            'description': 'Не працює коліщатко',
            'is_warranty': False,
            'date_received': '2024-12-15',
            'status': 'completed',
            'cost': 500.00
        }
    ]
    return JsonResponse({'repairs': repairs_data})


def api_repair_detail(request, repair_id):
    repair = {
        'id': repair_id,
        'customer': 'Олександр Сидоренко',
        'product': 'NVIDIA RTX 4070',
        'description': 'Не запускається, чорний екран',
        'diagnosis': 'Пошкоджений чіп пам\'яті GDDR6X',
        'repair_work': 'Заміна чіпа пам\'яті',
        'is_warranty': True,
        'date_received': '2024-12-18',
        'estimated_completion': '2024-12-25',
        'status': 'repairing',
        'cost': 0.00,
        'parts_used': []
    }
    return JsonResponse({'repair': repair})


# Гарантії
def api_warranties_list(request):
    warranties_data = [
        {
            'id': '674f1a2b8d4c5e12345678a8',
            'customer': 'Іван Іваненко',
            'product': 'Intel Core i7-13700K',
            'start_date': '2024-12-20',
            'end_date': '2027-12-20',
            'warranty_months': 36,
            'is_active': True
        },
        {
            'id': '674f1a2b8d4c5e12345678a9',
            'customer': 'Марія Петрівна',
            'product': 'NVIDIA RTX 4070',
            'start_date': '2024-11-15',
            'end_date': '2026-11-15',
            'warranty_months': 24,
            'is_active': True
        }
    ]
    return JsonResponse({'warranties': warranties_data})


# Послуги
def api_services_list(request):
    services_data = [
        {
            'id': '674f1a2b8d4c5e12345678aa',
            'customer': 'Олександр Сидоренко',
            'employee': 'Ігор Коваленко',
            'service_type': 'Встановлення Windows 11',
            'date_scheduled': '2024-12-22',
            'duration_hours': 2.5,
            'cost': 800.00,
            'status': 'scheduled'
        },
        {
            'id': '674f1a2b8d4c5e12345678ab',
            'customer': 'Іван Іваненко',
            'employee': 'Тетяна Шевченко',
            'service_type': 'Налаштування офісного ПЗ',
            'date_scheduled': '2024-12-21',
            'duration_hours': 3.0,
            'cost': 1200.00,
            'status': 'completed'
        }
    ]
    return JsonResponse({'services': services_data})


# Збірка ПК
def api_custom_pc_list(request):
    custom_pcs_data = [
        {
            'id': '674f1a2b8d4c5e12345678ac',
            'customer': 'Олександр Сидоренко',
            'employee': 'Роман Ткаченко',
            'pc_name': 'Gaming Beast 2024',
            'total_cost': 85000.00,
            'assembly_date': '2024-12-23',
            'status': 'components_ready',
            'components_count': 8
        },
        {
            'id': '674f1a2b8d4c5e12345678ad',
            'customer': 'Марія Петрівна',
            'employee': 'Роман Ткаченко',
            'pc_name': 'Office Pro Max',
            'total_cost': 45000.00,
            'assembly_date': '2024-12-15',
            'status': 'completed',
            'components_count': 6
        }
    ]
    return JsonResponse({'custom_pcs': custom_pcs_data})


# Співробітники
def api_employees_list(request):
    employees_data = [
        {
            'id': '674f1a2b8d4c5e12345678ae',
            'first_name': 'Олексій',
            'last_name': 'Мельник',
            'position': 'Менеджер з продажу',
            'phone': '+380671234567',
            'email': 'oleksiy.melnyk@company.ua',
            'hire_date': '2022-03-15',
            'is_active': True,
            'sales_count': 45,
            'total_sales_amount': 850000.00
        },
        {
            'id': '674f1a2b8d4c5e12345678af',
            'first_name': 'Світлана',
            'last_name': 'Коваль',
            'position': 'Менеджер з продажу',
            'phone': '+380509876543',
            'email': 'svitlana.koval@company.ua',
            'hire_date': '2023-01-10',
            'is_active': True,
            'sales_count': 38,
            'total_sales_amount': 720000.00
        },
        {
            'id': '674f1a2b8d4c5e12345678b0',
            'first_name': 'Роман',
            'last_name': 'Ткаченко',
            'position': 'Технік з збірки',
            'phone': '+380631357911',
            'email': 'roman.tkachenko@company.ua',
            'hire_date': '2021-09-20',
            'is_active': True,
            'assemblies_count': 25
        }
    ]
    return JsonResponse({'employees': employees_data})


# API звітів
def api_report_suppliers_products(request):
    # Звіт 1: Постачальники та їх продукція + комплектуючі від 2+ постачальників
    data = {
        'suppliers_products': [
            {
                'supplier': 'ТехноТрейд',
                'products': ['Intel Core i7-13700K', 'ASUS ROG Strix B550-F Gaming', 'Kingston FURY 16GB DDR4'],
                'products_count': 15
            },
            {
                'supplier': 'КомпАльянс',
                'products': ['NVIDIA RTX 4070', 'Samsung 970 EVO Plus 1TB', 'Intel Core i7-13700K'],
                'products_count': 12
            }
        ],
        'multi_supplier_components': [
            {
                'component': 'Intel Core i7-13700K',
                'suppliers': ['ТехноТрейд', 'КомпАльянс'],
                'suppliers_count': 2
            }
        ]
    }
    return JsonResponse(data)


def api_report_customers_by_manufacturer(request):
    # Звіт 2: Клієнти за виробником
    manufacturer = request.GET.get('manufacturer', 'Intel')
    data = {
        'manufacturer': manufacturer,
        'customers': [
            {
                'customer': 'Іван Іваненко',
                'phone': '+380671111111',
                'email': 'ivan.ivanenko@example.com',
                'products': ['Intel Core i7-13700K'],
                'total_amount': 15000.00
            },
            {
                'customer': 'Олександр Сидоренко',
                'phone': '+380633333333',
                'email': 'alex.sydorenko@example.com',
                'products': ['Intel Core i5-12400F', 'Intel Core i7-13700K'],
                'total_amount': 28000.00
            }
        ]
    }
    return JsonResponse(data)


def api_report_warranty_repairs(request):
    # Звіт 3: Гарантійні ремонти
    data = {
        'warranty_returns': [
            {
                'product': 'NVIDIA RTX 4070',
                'customer': 'Олександр Сидоренко',
                'return_date': '2024-12-18',
                'description': 'Не запускається, чорний екран',
                'status': 'repairing'
            },
            {
                'product': 'Samsung SSD 970 EVO',
                'customer': 'Марія Петрівна',
                'return_date': '2024-12-10',
                'description': 'Повільна робота системи',
                'status': 'completed'
            }
        ],
        'warranty_completed': [
            {
                'product': 'Samsung SSD 970 EVO',
                'customer': 'Марія Петрівна',
                'repair_date': '2024-12-12',
                'work_performed': 'Прошивка firmware, оптимізація',
                'cost': 0.00
            }
        ],
        'all_warranty_repairs': [
            {
                'repair_id': '674f1a2b8d4c5e12345678a6',
                'product': 'NVIDIA RTX 4070',
                'customer': 'Олександр Сидоренко',
                'date_received': '2024-12-18',
                'status': 'repairing',
                'estimated_completion': '2024-12-25'
            },
            {
                'repair_id': '674f1a2b8d4c5e12345678b1',
                'product': 'Samsung SSD 970 EVO',
                'customer': 'Марія Петрівна',
                'date_received': '2024-12-10',
                'status': 'completed',
                'completion_date': '2024-12-12'
            }
        ]
    }
    return JsonResponse(data)


def api_report_sales_analytics(request):
    # Звіт 4: Аналітика продажів
    month = request.GET.get('month', '2024-12')
    data = {
        'max_revenue_month': {
            'month': month,
            'revenue': 450000.00,
            'orders_count': 25
        },
        'weekly_sales_by_type': [
            {
                'product_type': 'component',
                'revenue': 180000.00,
                'quantity': 45
            },
            {
                'product_type': 'peripheral',
                'revenue': 25000.00,
                'quantity': 12
            },
            {
                'product_type': 'laptop',
                'revenue': 85000.00,
                'quantity': 3
            }
        ],
        'sales_by_employee': [
            {
                'employee': 'Олексій Мельник',
                'total_amount': 180000.00,
                'orders_count': 15,
                'products_sold': 35
            },
            {
                'employee': 'Світлана Коваль',
                'total_amount': 145000.00,
                'orders_count': 12,
                'products_sold': 28
            },
            {
                'employee': 'Ігор Коваленко',
                'total_amount': 125000.00,
                'orders_count': 8,
                'products_sold': 22
            }
        ]
    }
    return JsonResponse(data)


def api_report_components_by_price(request):
    # Звіт 5: Комплектуючі за ціною
    max_price = float(request.GET.get('max_price', 10000))
    data = {
        'max_price': max_price,
        'components': [
            {
                'name': 'Samsung 970 EVO Plus 1TB',
                'category': 'SSD накопичувачі',
                'price': 3500.00,
                'quantity_in_stock': 25,
                'manufacturer': 'Samsung'
            },
            {
                'name': 'Kingston FURY 16GB DDR4',
                'category': 'Оперативна пам\'ять',
                'price': 5000.00,
                'quantity_in_stock': 30,
                'manufacturer': 'Kingston'
            },
            {
                'name': 'ASUS ROG Strix B550-F',
                'category': 'Материнські плати',
                'price': 8000.00,
                'quantity_in_stock': 12,
                'manufacturer': 'ASUS'
            }
        ]
    }
    return JsonResponse(data)


def api_report_suppliers_repair_frequency(request):
    # Звіт 6: Постачальники за частотою ремонтів
    data = {
        'suppliers_repair_stats': [
            {
                'supplier': 'ТехноТрейд',
                'total_products_supplied': 150,
                'repair_cases': 8,
                'repair_rate': 5.33,
                'most_problematic_products': ['ASUS ROG Strix B550-F Gaming', 'Kingston FURY DDR4']
            },
            {
                'supplier': 'КомпАльянс',
                'total_products_supplied': 120,
                'repair_cases': 12,
                'repair_rate': 10.0,
                'most_problematic_products': ['NVIDIA RTX 4070', 'Samsung 970 EVO Plus']
            },
            {
                'supplier': 'ДіджіталПлюс',
                'total_products_supplied': 85,
                'repair_cases': 2,
                'repair_rate': 2.35,
                'most_problematic_products': ['Logitech MX Master 3']
            }
        ]
    }
    return JsonResponse(data)


def api_report_custom_pc_components(request):
    # Звіт 7: Компоненти збірки ПК
    customer_name = request.GET.get('customer', 'Олександр Сидоренко')
    data = {
        'customer': customer_name,
        'custom_pcs': [
            {
                'pc_name': 'Gaming Beast 2024',
                'assembly_date': '2024-12-23',
                'components': [
                    {
                        'component': 'Intel Core i7-13700K',
                        'category': 'Процесор',
                        'quantity': 1,
                        'price': 15000.00,
                        'purpose': 'CPU'
                    },
                    {
                        'component': 'NVIDIA RTX 4070',
                        'category': 'Відеокарта',
                        'quantity': 1,
                        'price': 22000.00,
                        'purpose': 'GPU'
                    },
                    {
                        'component': 'ASUS ROG Strix B550-F',
                        'category': 'Материнська плата',
                        'quantity': 1,
                        'price': 8000.00,
                        'purpose': 'Motherboard'
                    },
                    {
                        'component': 'Kingston FURY 32GB DDR4',
                        'category': 'ОЗУ',
                        'quantity': 2,
                        'price': 8000.00,
                        'purpose': 'RAM'
                    }
                ],
                'total_cost': 85000.00
            }
        ]
    }
    return JsonResponse(data)


def api_report_supplier_deliveries(request):
    # Звіт 8: Поставки від постачальників
    product_name = request.GET.get('product', 'Intel Core i7-13700K')
    start_date = request.GET.get('start_date', '2024-11-01')
    end_date = request.GET.get('end_date', '2024-12-31')

    data = {
        'product': product_name,
        'period': {'start_date': start_date, 'end_date': end_date},
        'deliveries': [
            {
                'supplier': 'ТехноТрейд',
                'contract_number': 'DOG-2024-001',
                'delivery_date': '2024-12-15',
                'quantity': 10,
                'unit_price': 15000.00,
                'total_amount': 150000.00
            },
            {
                'supplier': 'КомпАльянс',
                'contract_number': 'DOG-2024-003',
                'delivery_date': '2024-11-25',
                'quantity': 5,
                'unit_price': 14800.00,
                'total_amount': 74000.00
            }
        ],
        'total_quantity': 15,
        'total_amount': 224000.00
    }
    return JsonResponse(data)


def api_report_contracts_period(request):
    # Звіт 9: Договори за період
    start_date = request.GET.get('start_date', '2024-12-01')
    end_date = request.GET.get('end_date', '2024-12-31')

    data = {
        'period': {'start_date': start_date, 'end_date': end_date},
        'contracts': [
            {
                'number': 'DOG-2024-001',
                'supplier': 'ТехноТрейд',
                'date_signed': '2024-12-01',
                'delivery_date': '2024-12-15',
                'total_amount': 250000.00,
                'status': 'completed',
                'products_count': 5
            },
            {
                'number': 'DOG-2024-002',
                'supplier': 'КомпАльянс',
                'date_signed': '2024-12-10',
                'delivery_date': '2024-12-25',
                'total_amount': 180000.00,
                'status': 'active',
                'products_count': 3
            },
            {
                'number': 'DOG-2024-003',
                'supplier': 'ДіджіталПлюс',
                'date_signed': '2024-12-15',
                'delivery_date': '2025-01-05',
                'total_amount': 95000.00,
                'status': 'active',
                'products_count': 8
            }
        ],
        'contracts_by_supplier': [
            {'supplier': 'ТехноТрейд', 'contracts_count': 1, 'total_amount': 250000.00},
            {'supplier': 'КомпАльянс', 'contracts_count': 1, 'total_amount': 180000.00},
            {'supplier': 'ДіджіталПлюс', 'contracts_count': 1, 'total_amount': 95000.00}
        ],
        'total_contracts': 3,
        'total_amount': 525000.00
    }
    return JsonResponse(data)


def api_report_supplier_by_contract(request):
    # Звіт 10: Постачальник за номером договору
    contract_number = request.GET.get('contract_number', 'DOG-2024-001')

    data = {
        'contract_number': contract_number,
        'supplier': {
            'name': 'ТехноТрейд',
            'contact_person': 'Петренко Олег Васильович',
            'phone': '+380671234567',
            'email': 'info@technotrade.ua',
            'address': 'м. Київ, вул. Хрещатик, 1, оф. 205'
        },
        'contract_details': {
            'date_signed': '2024-12-01',
            'delivery_date': '2024-12-15',
            'total_amount': 250000.00,
            'status': 'completed',
            'products': [
                {
                    'name': 'Intel Core i7-13700K',
                    'quantity': 10,
                    'unit_price': 15000.00,
                    'total_price': 150000.00
                },
                {
                    'name': 'ASUS ROG Strix B550-F Gaming',
                    'quantity': 12,
                    'unit_price': 8333.33,
                    'total_price': 100000.00
                }
            ]
        }
    }
    return JsonResponse(data)