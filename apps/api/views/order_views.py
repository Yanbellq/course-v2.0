# apps/api/views/order_views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

from apps.crm.models import Sale, Employee, Product
from apps.main.models import User
from apps.crm.serializers.sale_serializer import SaleSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """
    Створення замовлення з корзини
    Очікує:
    {
        "products": [
            {"product_id": "...", "quantity": 1, "unit_price": 100.0}
        ],
        "payment_method": "card" | "cash" | "transfer",
        "delivery_address": "Адреса доставки",
        "notes": "Додаткові примітки (опціонально)"
    }
    """
    try:
        user_id = request.user.id
        
        # Отримуємо дані з запиту
        products_data = request.data.get('products', [])
        payment_method = request.data.get('payment_method', 'card')
        delivery_address = request.data.get('delivery_address', '')
        notes = request.data.get('notes', '')
        
        # Валідація
        if not products_data:
            return Response({
                'success': False,
                'error': 'Корзина порожня'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Знаходимо або створюємо employee для онлайн-замовлень
        # Шукаємо активного працівника з позицією sales або manager
        employee = Employee.objects().filter(
            is_active=True
        ).filter(
            position__in=['sales', 'manager', 'operator']
        ).first()
        
        if not employee:
            # Якщо немає активного працівника, беремо першого активного
            employee = Employee.objects().filter(is_active=True).first()
        
        if not employee:
            return Response({
                'success': False,
                'error': 'Не знайдено активного працівника для обробки замовлення'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Валідація та обробка продуктів
        products = []
        total_amount = 0.0
        
        for item in products_data:
            product_id = item.get('product_id')
            quantity = int(item.get('quantity', 1))
            unit_price = float(item.get('unit_price', 0))
            
            if not product_id:
                continue
            
            # Перевіряємо, чи існує продукт
            product = Product.find_by_id(product_id)
            if not product:
                return Response({
                    'success': False,
                    'error': f'Продукт з ID {product_id} не знайдено'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Використовуємо ціну з продукту, якщо не вказана
            if unit_price == 0:
                unit_price = float(product.price or 0)
            
            products.append({
                'product_id': product_id,
                'quantity': quantity,
                'unit_price': unit_price
            })
            
            total_amount += quantity * unit_price
        
        if not products:
            return Response({
                'success': False,
                'error': 'Немає валідних продуктів у замовленні'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Створюємо замовлення (Sale)
        sale = Sale()
        sale.user_id = user_id
        sale.employee_id = employee.id
        sale.products = products
        sale.total_amount = round(total_amount, 2)
        sale.sale_date = datetime.now()
        sale.status = 'pending'  # Статус "Відправлено" для онлайн-замовлень
        sale.payment_method = payment_method
        sale.notes = notes or f'Онлайн замовлення. Адреса доставки: {delivery_address}' if delivery_address else 'Онлайн замовлення'
        
        # Розраховуємо дату закінчення гарантії (наприклад, через 1 рік)
        sale.warranty_end_date = datetime.now() + timedelta(days=365)
        
        sale.created_at = datetime.now()
        sale.updated_at = datetime.now()
        
        sale.save()
        
        # Серіалізуємо результат
        serializer = SaleSerializer(sale)
        
        return Response({
            'success': True,
            'message': 'Замовлення успішно створено',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

