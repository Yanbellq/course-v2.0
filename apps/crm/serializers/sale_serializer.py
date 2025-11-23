from rest_framework import serializers
from apps.crm.serializers.product_list_item_serializer import ProductListItemSerializer
from apps.crm.models import Sale, Supply, Contract, Supplier, Product, Employee
from apps.main.models import User, SoftwareServiceConfig, CustomBuildConfig
from bson import ObjectId
from datetime import datetime

# === CustomBuild serializer ===
class CustomBuildSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    products = ProductListItemSerializer(many=True, required=False)
    total_cost = serializers.FloatField(required=False, allow_null=True)
    assembly_date = serializers.DateTimeField(required=False, allow_null=True)
    completion_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# === CustomBuildConfig serializer ===
class CustomBuildConfigSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, required=False)
    purchased = serializers.BooleanField(required=False, default=False)
    data = CustomBuildSerializer(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    
    def to_representation(self, instance):
        """Конвертує dict або об'єкт моделі в представлення"""
        if instance is None:
            return None
        
        # Якщо це словник (з БД), повертаємо його напряму з обробкою
        if isinstance(instance, dict):
            result = {
                'purchased': instance.get('purchased', False),
                'data': instance.get('data', {}),
                'created_at': instance.get('created_at'),
                'updated_at': instance.get('updated_at'),
            }
            if 'id' in instance:
                result['id'] = str(instance['id'])
            
            # Обробка products в data для додавання product об'єктів та subtotal
            if result.get('data') and isinstance(result['data'], dict) and 'products' in result['data']:
                products = result['data']['products']
                if isinstance(products, list):
                    processed_products = []
                    for item in products:
                        if isinstance(item, dict):
                            product_id = item.get('product_id')
                            product = Product.find_by_id(product_id) if product_id else None
                            quantity = item.get('quantity', 0)
                            unit_price = item.get('unit_price', 0)
                            processed_products.append({
                                'product': product.to_dict() if product else None,
                                'product_id': str(product_id) if product_id else '',
                                'quantity': quantity,
                                'unit_price': unit_price,
                                'subtotal': round(float(quantity) * float(unit_price), 2),
                            })
                        else:
                            processed_products.append(item)
                    result['data']['products'] = processed_products
            
            return result
        
        # Якщо це об'єкт моделі
        result = {
            'purchased': getattr(instance, 'purchased', False),
            'created_at': getattr(instance, 'created_at', None),
            'updated_at': getattr(instance, 'updated_at', None),
        }
        if hasattr(instance, 'id'):
            result['id'] = str(instance.id)
        if hasattr(instance, 'data'):
            data = instance.data
            if isinstance(data, dict):
                # Обробка products для додавання product об'єктів та subtotal
                if 'products' in data and isinstance(data['products'], list):
                    processed_products = []
                    for item in data['products']:
                        if isinstance(item, dict):
                            product_id = item.get('product_id')
                            product = Product.find_by_id(product_id) if product_id else None
                            quantity = item.get('quantity', 0)
                            unit_price = item.get('unit_price', 0)
                            processed_products.append({
                                'product': product.to_dict() if product else None,
                                'product_id': str(product_id) if product_id else '',
                                'quantity': quantity,
                                'unit_price': unit_price,
                                'subtotal': round(float(quantity) * float(unit_price), 2),
                            })
                        else:
                            processed_products.append(item)
                    data['products'] = processed_products
                result['data'] = data
            elif hasattr(data, '__dict__'):
                result['data'] = data.__dict__
            else:
                result['data'] = {}
        return result


# === SoftwareService serializer ===
class SoftwareServiceSerializer(serializers.Serializer):
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    software_list = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    date_scheduled = serializers.DateTimeField(required=False, allow_null=True)
    date_completed = serializers.DateTimeField(required=False, allow_null=True)
    cost = serializers.FloatField(required=False, allow_null=True)
    status = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)


# === SoftwareServiceConfig serializer ===
class SoftwareServiceConfigSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, required=False)
    purchased = serializers.BooleanField(required=False, default=False)
    data = SoftwareServiceSerializer(required=False, allow_null=True)
    created_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    
    def to_representation(self, instance):
        """Конвертує dict або об'єкт моделі в представлення"""
        if instance is None:
            return None
        
        # Якщо це словник (з БД), повертаємо його напряму з обробкою
        if isinstance(instance, dict):
            result = {
                'purchased': instance.get('purchased', False),
                'data': instance.get('data', {}),
                'created_at': instance.get('created_at'),
                'updated_at': instance.get('updated_at'),
            }
            if 'id' in instance:
                result['id'] = str(instance['id'])
            return result
        
        # Якщо це об'єкт моделі
        result = {
            'purchased': getattr(instance, 'purchased', False),
            'created_at': getattr(instance, 'created_at', None),
            'updated_at': getattr(instance, 'updated_at', None),
        }
        if hasattr(instance, 'id'):
            result['id'] = str(instance.id)
        if hasattr(instance, 'data'):
            data = instance.data
            if isinstance(data, dict):
                result['data'] = data
            elif hasattr(data, '__dict__'):
                result['data'] = data.__dict__
            else:
                result['data'] = {}
        return result


# === Sale serializer ===
class SaleSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True, required=False)

    user_id = serializers.CharField(required=True)
    employee_id = serializers.CharField(required=True)
    products = ProductListItemSerializer(many=True, required=False, allow_empty=True)

    # Використовуємо SerializerMethodField для обчислення загальної вартості
    products_total_cost = serializers.SerializerMethodField()

    total_amount = serializers.FloatField(required=True)
    sale_date = serializers.DateTimeField(required=True)
    status = serializers.CharField(required=True)
    payment_method = serializers.CharField(required=True)
    custom_build_service = CustomBuildConfigSerializer(required=False, allow_null=True)
    software_service = SoftwareServiceConfigSerializer(required=False, allow_null=True)
    warranty_end_date = serializers.DateTimeField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    created_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)
    updated_at = serializers.DateTimeField(read_only=True, required=False, allow_null=True)

    def get_products_total_cost(self, obj):
        """Розраховує загальну вартість продуктів на основі quantity та unit_price"""
        products = getattr(obj, 'products', []) or []
        total_cost = sum(
            float(item.get("quantity", 0)) * float(item.get("unit_price", 0))
            for item in products
        )
        # Округлюємо результат
        return round(total_cost, 2)
    
    # --------------------------
    # REPRESENTATION
    # --------------------------

    def to_representation(self, instance):
        # Обробка custom_build_service
        custom_build_service_repr = None
        if instance.custom_build_service:
            try:
                # Зверніть увагу: тут ми використовуємо екземпляр серіалізатора для обробки
                custom_build_service_repr = CustomBuildConfigSerializer().to_representation(instance.custom_build_service)
            except Exception as e:
                # Якщо помилка при серіалізації, повертаємо базову структуру
                if isinstance(instance.custom_build_service, dict):
                    custom_build_service_repr = instance.custom_build_service
                else:
                    custom_build_service_repr = None
        
        # Обробка software_service
        software_service_repr = None
        if instance.software_service:
            try:
                # Зверніть увагу: тут ми використовуємо екземпляр серіалізатора для обробки
                software_service_repr = SoftwareServiceConfigSerializer().to_representation(instance.software_service)
            except Exception as e:
                # Якщо помилка при серіалізації, повертаємо базову структуру
                if isinstance(instance.software_service, dict):
                    software_service_repr = instance.software_service
                else:
                    software_service_repr = None
        
        # --- ФОРМУВАННЯ ФІНАЛЬНОГО СЛОВНИКА З ВИКЛИКОМ ОБЧИСЛЮВАЛЬНОГО ПОЛЯ ---
        
        # 1. Обчислюємо загальну вартість, використовуючи метод get_products_total_cost
        calculated_total_cost = self.get_products_total_cost(instance)

        return {
            "id": str(instance.id),
            # Завантаження повних об'єктів User та Employee
            "user": User.find_by_id(instance.user_id).to_dict() if User.find_by_id(instance.user_id) else str(instance.user_id),
            "user_id": str(instance.user_id),
            "employee": Employee.find_by_id(instance.employee_id).to_dict() if Employee.find_by_id(instance.employee_id) else str(instance.employee_id),
            "employee_id": str(instance.employee_id),

            # Ручна обробка products для додавання повного об'єкта product та subtotal
            "products": [
                {
                    "product": (Product.find_by_id(item.get("product_id")).to_dict() if Product.find_by_id(item.get("product_id")) else None) if item.get("product_id") else None,
                    "product_id": str(item.get("product_id", "")),
                    "quantity": item.get("quantity", 0),
                    "unit_price": item.get("unit_price", 0),
                    "subtotal": round(float(item.get("quantity", 0)) * float(item.get("unit_price", 0)), 2),
                }
                for item in (instance.products or [])
            ],

            # 2. Включаємо обчислене поле products_total_cost
            "products_total_cost": calculated_total_cost, 

            "total_amount": instance.total_amount,
            "sale_date": instance.sale_date,
            "status": instance.status,
            "payment_method": instance.payment_method,
            # Включення оброблених вкладених сервісів
            "custom_build_service": custom_build_service_repr,
            "software_service": software_service_repr,
            
            "warranty_end_date": instance.warranty_end_date,
            "notes": instance.notes,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }