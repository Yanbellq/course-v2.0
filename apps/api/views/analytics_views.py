# apps/crm/views_analytics.py  (або додай до існуючого файлу views.py)
from django.http import JsonResponse
from datetime import timedelta
from django.utils.timezone import now
import importlib

# Назви моделей-кандидатів. Якщо у тебе є точні назви — постав їх сюди першим.
CANDIDATE_SALES = ['Sale', 'Order', 'Delivery', 'ProductListItem', 'CustomBuild']
CANDIDATE_REPAIRS = ['Repair', 'ServiceRequest', 'CustomBuild', 'SoftwareService']
CANDIDATE_CUSTOMERS = ['Customer', 'User']
CANDIDATE_PRODUCT = ['Product', 'ProductListItem']

def _get_model(app_module, candidate_names):
    """
    Повертає першу знайдену модель з candidate_names у модулі app_module.
    Якщо не знайдено — повертає None.
    """
    for name in candidate_names:
        model = getattr(app_module, name, None)
        if model is not None:
            return model
    return None

def analytics_api(request):
    # імпортуємо модулі з моделей CRM (використовуй свій шлях, якщо інший)
    crm_models = importlib.import_module('apps.crm.models')  # або 'apps.main.models' залежно від проєкту
    app_models_main = importlib.import_module('apps.main.models')

    # знаходимо моделі (перші підходящі)
    SaleModel = _get_model(crm_models, CANDIDATE_SALES) or _get_model(app_models_main, CANDIDATE_SALES)
    RepairModel = _get_model(crm_models, CANDIDATE_REPAIRS) or _get_model(app_models_main, CANDIDATE_REPAIRS)
    CustomerModel = _get_model(crm_models, CANDIDATE_CUSTOMERS) or _get_model(app_models_main, CANDIDATE_CUSTOMERS)
    ProductModel = _get_model(crm_models, CANDIDATE_PRODUCT) or _get_model(app_models_main, CANDIDATE_PRODUCT)

    # --- Revenue per month (6 місяців) ---
    months = []
    revenue = []
    for i in range(6):
        # беремо початок місяця i місяців назад
        month_start = (now() - timedelta(days=30 * i)).replace(day=1)
        # груба межа наступного місяця
        month_end = (month_start + timedelta(days=32)).replace(day=1)

        months.append(month_start.strftime("%b %Y"))

        total_for_month = 0
        if SaleModel:
            try:
                # на твоїй ORM: objects().filter(...).all() повертає список моделей
                qs = SaleModel.objects().filter(created_at__gte=month_start, created_at__lt=month_end).all()
                # Спробуємо сумувати одне з поширених полів: total_price / total_cost / amount / price
                for item in qs:
                    for fld in ('total_price', 'total_cost', 'amount', 'price', 'total'):
                        if hasattr(item, fld):
                            val = getattr(item, fld) or 0
                            try:
                                total_for_month += float(val)
                                break
                            except Exception:
                                # пропускаємо неконвертовані значення
                                pass
            except Exception:
                # якщо filter/objects() інтерфейс відрізняється — ігноруємо
                total_for_month = 0

        revenue.append(total_for_month)

    # --- Sales per category (fallback) ---
    cat_labels = []
    cat_values = []
    if ProductModel:
        try:
            # Працюємо без агрегатів: підрахуємо кількість продуктів по category
            cats = {}
            for p in ProductModel.objects().all():
                # у твоєму Product category зберігається як рядок slug (дивився раніше)
                cat = getattr(p, 'category', None) or 'Uncategorized'
                cats[cat] = cats.get(cat, 0) + 1
            # перетворимо словник у списки
            for k, v in cats.items():
                cat_labels.append(k)
                cat_values.append(v)
        except Exception:
            pass

    # --- Repairs count breakdown (pending / in_progress / completed) ---
    repair_labels = ['pending', 'in_progress', 'completed']
    repair_counts = [0, 0, 0]
    if RepairModel:
        try:
            repair_counts[0] = RepairModel.objects().filter(status='pending').count()
            repair_counts[1] = RepairModel.objects().filter(status='in_progress').count()
            repair_counts[2] = RepairModel.objects().filter(status='completed').count()
        except Exception:
            # деякі моделі можуть мати інші статуси — тоді просто рахунок усіх
            try:
                repair_counts = [RepairModel.objects().count(), 0, 0]
            except Exception:
                repair_counts = [0,0,0]

    # --- New customers per month ---
    cust_labels = []
    cust_values = []
    for i in range(6):
        month_start = (now() - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        cust_labels.append(month_start.strftime("%b %Y"))
        if CustomerModel:
            try:
                cust_values.append(CustomerModel.objects().filter(created_at__gte=month_start, created_at__lt=month_end).count())
            except Exception:
                # якщо User model (із apps.main.models) — можна спробувати role != 'admin'
                try:
                    # якщо CustomerModel == User, підрахуємо не-адмінів
                    if getattr(CustomerModel, '__name__', '') == 'User':
                        qs = CustomerModel.objects().filter(created_at__gte=month_start, created_at__lt=month_end).all()
                        cnt = 0
                        for u in qs:
                            if getattr(u, 'role', 'user') != 'admin':
                                cnt += 1
                        cust_values.append(cnt)
                    else:
                        cust_values.append(0)
                except Exception:
                    cust_values.append(0)
        else:
            cust_values.append(0)

    # Повертаємо результати (зворотній порядок щоб від найстарішого до останнього місяця)
    return JsonResponse({
        "revenue_months": months[::-1],
        "revenue_values": revenue[::-1],
        "category_labels": cat_labels,
        "category_sales": cat_values,
        "repair_labels": repair_labels,
        "repair_counts": repair_counts,
        "customer_labels": cust_labels[::-1],
        "customer_counts": cust_values[::-1],
    })
