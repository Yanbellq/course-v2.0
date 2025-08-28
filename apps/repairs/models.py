from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.customers.models import Customer
from apps.employees.models import Employee
from apps.products.models import Product
from apps.warranties.models import Warranty


# Ремонти
class Repair(Document):
    STATUS_CHOICES = [
        ('received', 'Прийнято'),
        ('diagnosed', 'Діагностовано'),
        ('repairing', 'Ремонтується'),
        ('completed', 'Завершено'),
        ('returned', 'Повернено клієнту'),
        ('cancelled', 'Скасовано')
    ]

    customer = fields.ReferenceField(Customer, required=True)
    product = fields.ReferenceField(Product, required=True)
    warranty = fields.ReferenceField(Warranty)  # Якщо гарантійний ремонт
    employee = fields.ReferenceField(Employee)  # Виконавець
    description = fields.StringField(required=True)
    diagnosis = fields.StringField()
    repair_work = fields.StringField()
    is_warranty = fields.BooleanField(default=False)
    date_received = fields.DateTimeField(default=datetime.utcnow)
    estimated_completion = fields.DateTimeField()
    actual_completion = fields.DateTimeField()
    status = fields.StringField(max_length=20, choices=STATUS_CHOICES, default='received')
    cost = fields.DecimalField(min_value=0, precision=2, default=0)
    parts_used = fields.ListField(fields.DictField())  # [{product_id, quantity, price}]

    meta = {
        'collection': 'repairs',
        'indexes': ['customer', 'product', 'status', 'date_received']
    }

