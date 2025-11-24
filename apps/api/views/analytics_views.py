# apps/api/views/analytics_views.py
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from apps.crm.models import Sale, Repair
from apps.main.models import User, Product

def analytics_api(request):
    now = timezone.now()

    # --- Revenue per month (6 місяців) ---
    months = []
    revenue = []
    for i in range(6):
        # беремо початок місяця i місяців назад
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # груба межа наступного місяця
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)

        months.append(month_start.strftime("%b %Y"))

        total_for_month = 0
        try:
            # Фільтруємо продажі за sale_date та сумуємо total_amount
            sales = Sale.objects().filter(
                sale_date__gte=month_start,
                sale_date__lt=month_end,
                status__in=['paid', 'pending']
            ).all()
            total_for_month = sum(float(sale.total_amount or 0) for sale in sales)
        except Exception:
            total_for_month = 0

        revenue.append(total_for_month)

    # --- Sales per category (продажі по категоріям продуктів) ---
    cat_labels = []
    cat_values = []
    try:
        # Підраховуємо продажі по категоріям продуктів
        cats = {}
        sales = Sale.objects().filter(status__in=['paid', 'pending']).all()
        for sale in sales:
            if hasattr(sale, 'products') and sale.products:
                for product_item in sale.products:
                    if isinstance(product_item, dict):
                        product_id = product_item.get('product_id')
                    else:
                        product_id = getattr(product_item, 'product_id', None)
                    
                    if product_id:
                        try:
                            product = Product.find_by_id(str(product_id))
                            if product:
                                cat = getattr(product, 'category', 'Uncategorized')
                                quantity = product_item.get('quantity', 0) if isinstance(product_item, dict) else getattr(product_item, 'quantity', 0)
                                cats[cat] = cats.get(cat, 0) + int(quantity or 0)
                        except Exception:
                            pass
        
        # Перетворимо словник у списки
        for k, v in sorted(cats.items(), key=lambda x: x[1], reverse=True)[:10]:  # Топ 10 категорій
            cat_labels.append(k)
            cat_values.append(v)
    except Exception:
        pass

    # --- Repairs count breakdown (by status) ---
    repair_labels = ['Received', 'Diagnosed', 'Repairing', 'Completed', 'Returned']
    repair_counts = [0, 0, 0, 0, 0]
    try:
        repair_counts[0] = Repair.objects().filter(status='received').count()
        repair_counts[1] = Repair.objects().filter(status='diagnosed').count()
        repair_counts[2] = Repair.objects().filter(status='repairing').count()
        repair_counts[3] = Repair.objects().filter(status='completed').count()
        repair_counts[4] = Repair.objects().filter(status='returned').count()
    except Exception:
        repair_counts = [0, 0, 0, 0, 0]

    # --- New customers per month (користувачі з role='user') ---
    cust_labels = []
    cust_values = []
    for i in range(6):
        month_start = (now - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        cust_labels.append(month_start.strftime("%b %Y"))
        
        try:
            # Підраховуємо користувачів з role='user' (не адмінів та не операторів)
            users = User.objects().filter(
                created_at__gte=month_start,
                created_at__lt=month_end,
                role='user'
            ).all()
            cust_values.append(len(users))
        except Exception:
            cust_values.append(0)

    # Повертаємо результати (зворотній порядок щоб від найстарішого до останнього місяця)
    result = {
        "revenue_months": months[::-1] if months else [],
        "revenue_values": revenue[::-1] if revenue else [],
        "category_labels": cat_labels if cat_labels else [],
        "category_sales": cat_values if cat_values else [],
        "repair_labels": repair_labels if repair_labels else [],
        "repair_counts": repair_counts if repair_counts else [],
        "customer_labels": cust_labels[::-1] if cust_labels else [],
        "customer_counts": cust_values[::-1] if cust_values else [],
    }
    
    return JsonResponse(result)
