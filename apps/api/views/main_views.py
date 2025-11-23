# apps/api/views/main_views.py

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps import api
from apps.api.authentication.permissions import IsAdminOrReadOnly
from apps.main.models import ProductCategory, Product, ProductListItem

from apps.api.serializers.main_serializers import ProductCategorySerializer
from apps.api.serializers.main_serializers import ProductViewSerializer, ProductSerializer

# ====== ProductCategory Views ======

@api_view(['GET'])
@permission_classes([AllowAny])
def list_product_categories(request):
    # Список всіх категорій
    categories = ProductCategory.objects().all()
    data = [ProductCategorySerializer(c).data for c in categories]
    return Response(data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_product_category(request, pk):
    category = ProductCategory.find_by_id(pk)
    if not category:
        return Response({'error': 'Категорію не знайдено!'}, status=status.HTTP_404_NOT_FOUND)
    return Response(ProductCategorySerializer(category).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product_category(request):
    serializer = ProductCategorySerializer(data=request.data)
    if serializer.is_valid():
        item = serializer.save()
        return Response(ProductCategorySerializer(item).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminOrReadOnly])
def update_product_category(request, pk):
    category = ProductCategory.find_by_id(pk)
    if not category:
        return Response({'error': 'Категорію не знайдено!'}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductCategorySerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        item = serializer.save()
        return Response(ProductCategorySerializer(item).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminOrReadOnly])
def delete_product_category(request, pk):
    category = ProductCategory.find_by_id(pk)
    if not category:
        return Response({'error': 'Категорію не знайдено!'}, status=status.HTTP_404_NOT_FOUND)
    category.delete()
    return Response({'success': True})


# ====== Product Views ======

@api_view(['GET'])
@permission_classes([AllowAny])
def list_products(request):
    """
    Список продуктів з фільтрацією
    
    Query параметри:
    - category: slug категорії
    - price_min: Мінімальна ціна
    - price_max: Максимальна ціна
    - search: Пошук по назві
    - in_stock: true/false (в наявності)
    - sort_by: price, -price, created_at, -created_at, name, -name
    - limit: Кількість результатів
    - skip: Пропустити N записів
    """
    products = Product.objects()
    
    # Фільтри (як раніше)
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    price_min = request.GET.get('price_min')
    if price_min:
        try:
            products = products.filter(price__gte=float(price_min))
        except ValueError:
            return Response({'error': 'price_min має бути числом'}, status=400)
    
    price_max = request.GET.get('price_max')
    if price_max:
        try:
            products = products.filter(price__lte=float(price_max))
        except ValueError:
            return Response({'error': 'price_max має бути числом'}, status=400)
    
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
    product_type = request.GET.get('product_type')
    if product_type:
        products = products.filter(product_type=product_type)
    
    # Сортування
    sort_by = request.GET.get('sort_by', '-created_at')
    products = products.order_by(sort_by)
    
    # Пагінація
    limit = request.GET.get('limit')
    if limit:
        try:
            products = products.limit(int(limit))
        except ValueError:
            return Response({'error': 'limit має бути числом'}, status=400)
    
    skip = request.GET.get('skip')
    if skip:
        try:
            products = products.skip(int(skip))
        except ValueError:
            return Response({'error': 'skip має бути числом'}, status=400)
    
    # Отримуємо результати
    product_list = products.all()
    data = [ProductViewSerializer(p).data for p in product_list]
    
    return Response({
        'count': len(data),
        'results': data
    })


@api_view(['GET'])
def get_product(request, pk):
    """Отримати один продукт"""
    product = Product.find_by_id(pk)
    if not product:
        return Response(
            {'error': 'Продукт не знайдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    return Response(ProductViewSerializer(product).data)


@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def create_product(request):
    """Створити продукт"""
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        product = serializer.save()
        return Response(
            ProductViewSerializer(product).data,
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAdminOrReadOnly])
def update_product(request, pk):
    """Оновити продукт"""
    product = Product.find_by_id(pk)
    if not product:
        return Response(
            {'error': 'Продукт не знайдено'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ProductSerializer(
        instance=product,
        data=request.data,
        partial=True
    )
    if serializer.is_valid():
        product = serializer.save()
        return Response(ProductViewSerializer(product).data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminOrReadOnly])
def delete_product(request, pk):
    """Видалити продукт"""
    product = Product.find_by_id(pk)
    if not product:
        return Response({'error': 'Продукт не знайдено!'}, status=status.HTTP_404_NOT_FOUND)
    product.delete()
    return Response({'success': True})


@api_view(['GET'])
@permission_classes([AllowAny])
def search_products(request):
    query = request.GET.get('q', '').strip().lower()

    if len(query) < 3:
        return Response({'results': []})

    # Mongo-style пошук
    products_queryset = Product.objects().filter( name__icontains=query ).limit(10)

    results = []
    for p in products_queryset.all():
        data = ProductViewSerializer(p).data
        results.append(data)

    return Response({'results': results})
