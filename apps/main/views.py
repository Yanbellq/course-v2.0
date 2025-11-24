from django.shortcuts import render
from apps.main.models import User, ProductCategory, Product, ProductListItem, SoftwareService, SoftwareServiceConfig, CustomBuild, CustomBuildConfig, Delivery
from apps.crm.models import Supplier, Supply, Sale, Contract, Employee, Repair

from apps.api.serializers.main_serializers import ProductCategorySerializer
from apps.api.serializers.main_serializers import ProductViewSerializer

def dashboard(request):
    # Отримуємо всі категорії
    categories_list = ProductCategory.objects().all()
    products__list = Product.objects().order_by('-created_at').limit(8)

    # Сортуємо так:
    # 1. Алфавітно по slug
    # 2. Але "other" завжди останній
    categories_sorted = sorted(
        categories_list,
        key=lambda c: (c.slug == 'other', c.slug.lower())
    )

    # Серіалізуємо
    categories = [ProductCategorySerializer(c).data for c in categories_sorted]
    products = [ProductViewSerializer(p).data for p in products__list.all()]

    context = {
        'categories': categories,
        'products': products
    }

    return render(request, 'user/index.html', context)


def auth(request):
    categories_list = ProductCategory.objects().all()

    categories_sorted = sorted(
        categories_list,
        key=lambda c: (c.slug == 'other', c.slug.lower())
    )

    categories = [ProductCategorySerializer(c).data for c in categories_sorted]

    # Get next URL from query parameter for redirect after login
    next_url = request.GET.get('next', '/')
    
    # Get reset password token from query parameter
    reset_token = request.GET.get('token', None)
    
    # Get auth message from session (set by middleware)
    auth_message = None
    auth_message_type = None
    if 'auth_message' in request.session:
        auth_message = request.session.pop('auth_message')
        auth_message_type = request.session.pop('auth_message_type', 'info')

    context = {
        'categories': categories,
        'next_url': next_url,
        'auth_message': auth_message,
        'auth_message_type': auth_message_type,
        'reset_token': reset_token
    }
    return render(request, 'user/auth.html', context)

def profile(request):
    categories_list = ProductCategory.objects().all()

    categories_sorted = sorted(
        categories_list,
        key=lambda c: (c.slug == 'other', c.slug.lower())
    )

    categories = [ProductCategorySerializer(c).data for c in categories_sorted]

    context = {
        'categories': categories
    }
    return render(request, 'user/profile.html', context)

def categories(request):
    """Сторінка каталогу з фільтрацією"""
    
    # Отримуємо всі продукти
    products_queryset = Product.objects()

    # === ФІЛЬТРАЦІЯ ===
    # === 1️⃣ Категорія ===
    category_filter = request.GET.get('category')
    if category_filter and category_filter != 'all':
        products_queryset = products_queryset.filter(category=category_filter)

    # Усі продукти всередині категорії (для вибору типів)
    products_in_category = products_queryset.all()

    # === 2️⃣ Тип ===
    product_type_filter = request.GET.get('product_type')
    if product_type_filter and product_type_filter != 'all':
        products_queryset = products_queryset.filter(product_type=product_type_filter)

    # Усі продукти всередині типу (для вибору брендів)
    products_in_type = products_queryset.all()

    # === 3️⃣ Бренд ===
    brand_filter = request.GET.get('brand')
    if brand_filter and brand_filter != 'all':
        products_queryset = products_queryset.filter(manufacturer=brand_filter)

    # === 4️⃣ Ціна ===
    price_min = request.GET.get('min_price')
    price_max = request.GET.get('max_price')

    price_filter = {}
    try:
        if price_min:
            price_filter['price__gte'] = float(price_min)
        if price_max:
            price_filter['price__lte'] = float(price_max)
    except ValueError:
        price_filter = {}

    if price_filter:
        products_queryset = products_queryset.filter(**price_filter)
    

    # === СОРТУВАННЯ ===
    sort = request.GET.get('sort', 'latest')
    sort_mapping = {
        'latest': '-created_at',
        'price-low': 'price',
        'price-high': '-price',
        'name-asc': 'name',
        'name-desc': '-name',
    }
    sort_by = sort_mapping.get(sort, '-created_at')
    products_queryset = products_queryset.order_by(sort_by)
    
    # === ПАГІНАЦІЯ ===
    total_count = products_queryset.count()
    page = int(request.GET.get('page', 1))
    per_page = 15
    skip = (page - 1) * per_page
    products_queryset = products_queryset.skip(skip).limit(per_page)
    products_list = [ProductViewSerializer(p).data for p in products_queryset.all()]
    total_pages = (total_count + per_page - 1) // per_page
    

    # === ДАНІ ДЛЯ ФІЛЬТРІВ ===
    # === 7️⃣ Категорії ===
    categories_list = ProductCategory.objects().all()

    # Сортуємо так:
    # 1. Алфавітно по slug
    # 2. Але "other" завжди останній
    categories_sorted = sorted(
        categories_list,
        key=lambda c: (c.slug == 'other', c.slug.lower())
    )

    # === 8️⃣ Типи (залежать від категорії) ===
    types_set = set()
    for p in products_in_category:
        ser = ProductViewSerializer(p)
        t = ser.data.get('product_type_en') or ser.data.get('product_type')
        v = ser.data.get('product_type')
        if t:
            types_set.add((t, v))
    types = sorted(types_set)
    
    # === 9️⃣ Бренди (залежать від типу) ===
    brands_set = set(p.manufacturer for p in products_in_type if p.manufacturer)
    brands = sorted(brands_set)
    

    context = {
        'products': products_list,
        'categories': categories_sorted,
        'brands': brands,
        'types': types,
        # Поточні фільтри
        'current_category': category_filter or 'all',
        'current_brand': brand_filter or 'all',
        'current_min_price': price_min or '',
        'current_max_price': price_max or '',
        'current_type': product_type_filter or 'all',
        'current_sort': sort,
        # Пагінація
        'current_page': page,
        'total_pages': total_pages,
        'total_count': total_count,
    }
    
    return render(request, 'user/categories.html', context)


def product_detail(request, product_id):
    """Сторінка деталей продукту"""
    product = Product.find_by_id(product_id)
    ser = ProductViewSerializer(product)
    product_data = ser.data
    
    if not product:
        # Або 404 page
        return render(request, '404.html', status=404)
    
    # Related products (з тієї ж категорії)
    related_products = Product.objects().filter(
        category=product.category
    ).limit(4).all()
    
    # Видаляємо сам продукт зі списку related
    related_products = [p for p in related_products if str(p.id) != str(product.id)]
    
    context = {
        'product': product_data,
        'related_products': related_products[:4]  # Максимум 4
    }
    
    return render(request, 'user/product.html', context)
