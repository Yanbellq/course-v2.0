from bson import ObjectId
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.contracts.models import Contract
from apps.suppliers.models import Supplier


# Категорії товарів
class ProductCategory(Document):
    name = fields.StringField(max_length=100, required=True, unique=True)
    description = fields.StringField()
    parent_category = fields.ReferenceField('self')

    meta = {
        'collection': 'product_categories'
    }

# Товари
class Product(Document):
    PRODUCT_TYPES = [
        ('component', 'Комплектуючі'),
        ('peripheral', 'Периферійні пристрої'),
        ('laptop', 'Ноутбуки'),
        ('computer', 'Готові комп\'ютери'),
        ('software', 'Програмне забезпечення'),
    ]

    id = fields.StringField(primary_key=True, default=lambda: 'PROD-' + str(ObjectId()))
    name = fields.StringField(max_length=200, required=True)
    # category = fields.ReferenceField(ProductCategory, required=True)
    category = fields.StringField(required=True)
    product_type = fields.StringField(max_length=20, choices=PRODUCT_TYPES, required=True)
    manufacturer = fields.StringField(max_length=100, required=True)
    model = fields.StringField(max_length=100)
    specifications = fields.DictField()
    price = fields.FloatField(required=True, min_value=0)
    warranty_months = fields.IntField(min_value=0, default=12)
    quantity_in_stock = fields.IntField(min_value=0, default=0)
    min_stock_level = fields.IntField(min_value=0, default=5)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'products',
        'auto_create_index': False,
        'indexes': ['name', 'manufacturer', 'product_type', 'category']
    }

    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "category": self.category,
            "manufacturer": self.manufacturer,
            "price": self.price,
            "quantity_in_stock": self.quantity_in_stock,
            "min_stock_level": self.min_stock_level,
            "product_type": self.product_type,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

# Поставки
class ProductSupply(Document):
    contract = fields.ReferenceField(Contract, required=True)
    product = fields.ReferenceField(Product, required=True)
    supplier = fields.ReferenceField(Supplier, required=True)
    quantity = fields.IntField(min_value=1, required=True)
    unit_price = fields.DecimalField(min_value=0, precision=2, required=True)
    total_cost = fields.DecimalField(min_value=0, precision=2)
    delivery_date = fields.DateTimeField(required=True)
    received_date = fields.DateTimeField()
    status = fields.StringField(max_length=20, choices=[
        ('ordered', 'Замовлено'),
        ('delivered', 'Доставлено'),
        ('received', 'Отримано')
    ], default='ordered')

    meta = {
        'collection': 'product_supplies',
        'indexes': ['contract', 'product', 'supplier', 'delivery_date']
    }


