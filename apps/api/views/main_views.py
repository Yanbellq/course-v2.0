# apps/api/views/main_views.py

import threading
import logging
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
import re

from apps import api
from apps.api.authentication.permissions import IsAdminOrReadOnly
from apps.main.models import ProductCategory, Product, ProductListItem

from apps.api.serializers.main_serializers import ProductCategorySerializer
from apps.api.serializers.main_serializers import ProductViewSerializer, ProductSerializer
from apps.crm.models import Supplier, Employee
from apps.main.models import ProductCategory, Product

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


# ====== Newsletter Subscription ======

def send_newsletter_subscription_email(email):
    """
    Відправляє email з підтвердженням підписки на newsletter
    
    Args:
        email: Email адреса користувача
    """
    logger = logging.getLogger('api')
    
    try:
        # Перевірка налаштувань
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.warning(f"Email settings not configured. Newsletter email will not be sent to {email}.")
            logger.warning(f"EMAIL_HOST_USER: {bool(settings.EMAIL_HOST_USER)}, EMAIL_HOST_PASSWORD: {bool(settings.EMAIL_HOST_PASSWORD)}")
            return
        
        subject = 'Welcome to Our Newsletter - Electronic Store'
        
        # Контекст для шаблону
        context = {
            'email': email,
            'current_year': datetime.now().year,
        }
        
        # Рендеримо HTML та текстовий варіанти
        try:
            html_message = render_to_string('emails/newsletter_subscription.html', context)
            plain_message = render_to_string('emails/newsletter_subscription.txt', context)
        except Exception as e:
            logger.error(f"Failed to render newsletter email templates for {email}: {str(e)}")
            logger.exception(e)
            return
        
        # Логуємо деталі перед відправкою
        logger.info(f"Attempting to send newsletter subscription email to {email}")
        logger.debug(f"Email backend: {settings.EMAIL_BACKEND}")
        logger.debug(f"From: {settings.DEFAULT_FROM_EMAIL}")
        
        # Відправляємо email через Gmail SMTP
        result = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        if result:
            logger.info(f"Newsletter subscription email sent successfully to {email}")
        else:
            logger.error(f"Newsletter email sending returned False for {email} (check email settings)")
            
    except Exception as e:
        logger.error(f"Error sending newsletter email to {email}: {str(e)}")
        logger.exception(e)
        # Не піднімаємо помилку далі, щоб не ламати потік


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    """
    Підписка на newsletter
    """
    logger = logging.getLogger('api')
    logger.info(f"Newsletter subscription request received. Method: {request.method}, Data: {request.data}")
    
    email = request.data.get('email', '').strip().lower()
    
    # Валідація email
    if not email:
        logger.warning("Newsletter subscription: email is empty")
        return Response({
            'success': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Перевірка формату email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        logger.warning(f"Newsletter subscription: invalid email format - {email}")
        return Response({
            'success': False,
            'message': 'Invalid email format'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    logger.info(f"Newsletter subscription: processing subscription for {email}")
    
    # Відправляємо email в окремому потоці, щоб не блокувати відповідь
    try:
        email_thread = threading.Thread(
            target=send_newsletter_subscription_email,
            args=(email,),
            daemon=True
        )
        email_thread.start()
        logger.info(f"Newsletter subscription: email thread started for {email}")
        
        return Response({
            'success': True,
            'message': 'Thank you for subscribing! Please check your email for confirmation.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error processing newsletter subscription for {email}: {str(e)}")
        logger.exception(e)
        return Response({
            'success': False,
            'message': 'An error occurred while processing your subscription. Please try again later.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ====== Supplier Validation ======

@api_view(['POST'])
@permission_classes([AllowAny])
def check_supplier_email_unique(request):
    """Перевірка унікальності email постачальника"""
    email = request.data.get('email', '').strip().lower()
    supplier_id = request.data.get('supplier_id', '').strip()
    
    if not email:
        return Response({
            'unique': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Перевіряємо чи існує постачальник з таким email
    existing_supplier = Supplier.objects().filter(email=email).first()
    
    # Якщо редагуємо існуючого постачальника, ігноруємо його самого
    if existing_supplier and supplier_id and str(existing_supplier.id) == supplier_id:
        return Response({
            'unique': True,
            'message': 'Email is available'
        })
    
    return Response({
        'unique': existing_supplier is None,
        'message': 'Email already exists' if existing_supplier else 'Email is available'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_supplier_phone_unique(request):
    """Перевірка унікальності phone постачальника"""
    phone = request.data.get('phone', '').strip()
    supplier_id = request.data.get('supplier_id', '').strip()
    
    if not phone:
        return Response({
            'unique': False,
            'message': 'Phone is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Перевіряємо чи існує постачальник з таким phone
    existing_supplier = Supplier.objects().filter(phone=phone).first()
    
    # Якщо редагуємо існуючого постачальника, ігноруємо його самого
    if existing_supplier and supplier_id and str(existing_supplier.id) == supplier_id:
        return Response({
            'unique': True,
            'message': 'Phone is available'
        })
    
    return Response({
        'unique': existing_supplier is None,
        'message': 'Phone already exists' if existing_supplier else 'Phone is available'
    })


# ====== Product Category Validation ======

@api_view(['POST'])
@permission_classes([AllowAny])
def check_category_name_unique(request):
    """Перевірка унікальності name категорії"""
    name = request.data.get('name', '').strip()
    category_id = request.data.get('category_id', '').strip()
    
    if not name:
        return Response({
            'unique': False,
            'message': 'Name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_category = ProductCategory.objects().filter(name=name).first()
    
    if existing_category and category_id and str(existing_category.id) == category_id:
        return Response({
            'unique': True,
            'message': 'Name is available'
        })
    
    return Response({
        'unique': existing_category is None,
        'message': 'Name already exists' if existing_category else 'Name is available'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_category_slug_unique(request):
    """Перевірка унікальності slug категорії"""
    slug = request.data.get('slug', '').strip()
    category_id = request.data.get('category_id', '').strip()
    
    if not slug:
        return Response({
            'unique': False,
            'message': 'Slug is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_category = ProductCategory.objects().filter(slug=slug).first()
    
    if existing_category and category_id and str(existing_category.id) == category_id:
        return Response({
            'unique': True,
            'message': 'Slug is available'
        })
    
    return Response({
        'unique': existing_category is None,
        'message': 'Slug already exists' if existing_category else 'Slug is available'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_category_image_url_unique(request):
    """Перевірка унікальності image_url категорії"""
    image_url = request.data.get('image_url', '').strip()
    category_id = request.data.get('category_id', '').strip()
    
    if not image_url:
        return Response({
            'unique': False,
            'message': 'Image URL is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_category = ProductCategory.objects().filter(image_url=image_url).first()
    
    if existing_category and category_id and str(existing_category.id) == category_id:
        return Response({
            'unique': True,
            'message': 'Image URL is available'
        })
    
    return Response({
        'unique': existing_category is None,
        'message': 'Image URL already exists' if existing_category else 'Image URL is available'
    })


# ====== Product Validation ======

@api_view(['POST'])
@permission_classes([AllowAny])
def check_product_name_unique(request):
    """Перевірка унікальності name продукту"""
    name = request.data.get('name', '').strip()
    product_id = request.data.get('product_id', '').strip()
    
    if not name:
        return Response({
            'unique': False,
            'message': 'Name is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_product = Product.objects().filter(name=name).first()
    
    if existing_product and product_id and str(existing_product.id) == product_id:
        return Response({
            'unique': True,
            'message': 'Name is available'
        })
    
    return Response({
        'unique': existing_product is None,
        'message': 'Name already exists' if existing_product else 'Name is available'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_product_image_url_unique(request):
    """Перевірка унікальності image_url продукту"""
    image_url = request.data.get('image_url', '').strip()
    product_id = request.data.get('product_id', '').strip()
    
    if not image_url:
        return Response({
            'unique': False,
            'message': 'Image URL is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_product = Product.objects().filter(image_url=image_url).first()
    
    if existing_product and product_id and str(existing_product.id) == product_id:
        return Response({
            'unique': True,
            'message': 'Image URL is available'
        })
    
    return Response({
        'unique': existing_product is None,
        'message': 'Image URL already exists' if existing_product else 'Image URL is available'
    })


# ====== Employee Validation ======

@api_view(['POST'])
@permission_classes([AllowAny])
def check_employee_email_unique(request):
    """Перевірка унікальності email працівника"""
    email = request.data.get('email', '').strip().lower()
    employee_id = request.data.get('employee_id', '').strip()
    
    if not email:
        return Response({
            'unique': False,
            'message': 'Email is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_employee = Employee.objects().filter(email=email).first()
    
    if existing_employee and employee_id and str(existing_employee.id) == employee_id:
        return Response({
            'unique': True,
            'message': 'Email is available'
        })
    
    return Response({
        'unique': existing_employee is None,
        'message': 'Email already exists' if existing_employee else 'Email is available'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def check_employee_phone_unique(request):
    """Перевірка унікальності phone працівника"""
    phone = request.data.get('phone', '').strip()
    employee_id = request.data.get('employee_id', '').strip()
    
    if not phone:
        return Response({
            'unique': False,
            'message': 'Phone is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    existing_employee = Employee.objects().filter(phone=phone).first()
    
    if existing_employee and employee_id and str(existing_employee.id) == employee_id:
        return Response({
            'unique': True,
            'message': 'Phone is available'
        })
    
    return Response({
        'unique': existing_employee is None,
        'message': 'Phone already exists' if existing_employee else 'Phone is available'
    })
