from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.customers.models import Customer
from apps.employees.models import Employee
from apps.products.models import Product


# Позиція продажу
class SaleItem(EmbeddedDocument):
    product = fields.ReferenceField(Product, required=True)
    quantity = fields.IntField(min_value=1, required=True)
    unit_price = fields.DecimalField(min_value=0, precision=2, required=True)
    total_price = fields.DecimalField(min_value=0, precision=2)


# Продажі
class Sale(Document):
    customer = fields.ReferenceField(Customer, required=True)
    employee = fields.ReferenceField(Employee, required=True)
    sale_date = fields.DateTimeField(default=datetime.utcnow)
    items = fields.ListField(fields.EmbeddedDocumentField(SaleItem))
    total_amount = fields.DecimalField(min_value=0, precision=2)
    payment_method = fields.StringField(max_length=20, choices=[
        ('cash', 'Готівка'),
        ('card', 'Картка'),
        ('transfer', 'Переказ')
    ], default='cash')
    status = fields.StringField(max_length=20, choices=[
        ('pending', 'Очікує'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано')
    ], default='completed')

    meta = {
        'collection': 'sales',
        'indexes': ['customer', 'employee', 'sale_date']
    }


