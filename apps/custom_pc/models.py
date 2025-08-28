from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.customers.models import Customer
from apps.employees.models import Employee
from apps.sales.models import Sale


# Послуги налаштування ПЗ
class SoftwareService(Document):
    customer = fields.ReferenceField(Customer, required=True)
    employee = fields.ReferenceField(Employee, required=True)
    service_type = fields.StringField(max_length=200, required=True)
    description = fields.StringField(required=True)
    software_list = fields.ListField(fields.StringField())
    date_scheduled = fields.DateTimeField(required=True)
    date_completed = fields.DateTimeField()
    duration_hours = fields.FloatField(min_value=0)
    cost = fields.DecimalField(min_value=0, precision=2, required=True)
    status = fields.StringField(max_length=20, choices=[
        ('scheduled', 'Заплановано'),
        ('in_progress', 'Виконується'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано')
    ], default='scheduled')

    meta = {
        'collection': 'software_services',
        'indexes': ['customer', 'employee', 'date_scheduled']
    }


# Кастомна збірка ПК
class CustomPC(Document):
    customer = fields.ReferenceField(Customer, required=True)
    employee = fields.ReferenceField(Employee, required=True)
    sale = fields.ReferenceField(Sale)  # Пов'язаний продаж
    pc_name = fields.StringField(max_length=200)
    components = fields.ListField(fields.DictField())  # [{product_id, quantity, purpose}]
    total_cost = fields.DecimalField(min_value=0, precision=2)
    assembly_date = fields.DateTimeField()
    completion_date = fields.DateTimeField()
    status = fields.StringField(max_length=20, choices=[
        ('ordered', 'Замовлено'),
        ('components_ready', 'Компоненти готові'),
        ('assembling', 'Збирається'),
        ('testing', 'Тестується'),
        ('completed', 'Завершено'),
        ('delivered', 'Передано клієнту')
    ], default='ordered')
    notes = fields.StringField()

    meta = {
        'collection': 'custom_pcs',
        'indexes': ['customer', 'employee', 'assembly_date']
    }