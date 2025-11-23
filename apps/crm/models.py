# apps/crm/models.py

from email.policy import default
from random import choices
import core.mongo_orm as orm
from datetime import datetime

from apps.main.models import CustomBuildConfig, Product, ProductListItem, SoftwareServiceConfig, User

class Supplier(orm.Model):
    """Модель постачальника"""
    _collection_name = 'suppliers'

    name = orm.StringField(required=True, max_length=200)
    contact_person = orm.StringField(required=True, max_length=100)
    email = orm.EmailField(required=True, unique=True)
    phone = orm.PhoneField(required=True, max_length=20)
    address = orm.StringField()
    description = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class Contract(orm.Model):
    """Модель договору"""
    _collection_name = "contracts"

    STATUS_CHOICES = [
        ('active', 'Активний'),
        ('completed', 'Виконано'),
        ('cancelled', 'Скасовано')
    ]

    number = orm.StringField(required=True, unique=True, max_length=8)
    supplier_id = orm.ReferenceField(Supplier, required=True)
    total_amount = orm.FloatField(min_value=0)
    signing_date = orm.DateTimeField(required=True, default=datetime.now)
    products = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, unit_price}]
    status = orm.StringField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()

    @classmethod
    def generate_unique_number(cls):
        import random
        while True:
            num = str(random.randint(10_000_000, 99_999_999))  # 8 цифр
            if not cls.objects().filter(number=num).first():
                return num


class Supply(orm.Model):
    """Модель постачання товарів"""
    _collection_name = "supplies"

    STATUS_CHOICES = [
        ('ordered', 'Замовлено'),
        ('delivered', 'Доставлено'),
        ('received', 'Отримано'),
        ('cancelled', 'Повернено')
    ]

    contract_id = orm.ReferenceField(Contract, required=True)
    supplier_id = orm.ReferenceField(Supplier, required=True)
    products = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, unit_price}]
    total_cost = orm.FloatField(min_value=0)
    delivery_date = orm.DateTimeField(required=True, default=datetime.now)
    received_date = orm.DateTimeField()
    status = orm.StringField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    notes = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class Employee(orm.Model):
    """Модель працівника"""
    _collection_name = 'employees'

    POSITION_CHOICES = [
        ('manager', 'Менеджер'),
        ('technician', 'Технік'),
        ('sales', 'Менеджер з продажу'),
        ('support', 'Служба підтримки'),
        ('developer', 'Розробник'),
        ('designer', 'Дизайнер'),
        (' accountant', 'Бухгалтер'),
        ('hr', 'HR менеджер'),
        ('logistics', 'Логіст'),
        ('admin', 'Адміністратор'),
        ('operator', 'Оператор'),
        ('cleaner', 'Прибиральник'),
        ('security', 'Охоронець'),
    ]

    full_name = orm.StringField(required=True, max_length=200)
    position = orm.StringField(required=True, choices=POSITION_CHOICES, default='manager')
    email = orm.EmailField()
    phone = orm.PhoneField(max_length=20)
    hire_date = orm.DateTimeField()
    salary = orm.FloatField()
    is_active = orm.BooleanField(default=True)
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class Sale(orm.Model):
    """Модель продажу"""
    _collection_name = 'sales'

    STATUS_CHOICES = [
        ('paid', 'Оплачено'),
        ('pending', 'Відправлено'),
        ('cancelled', 'Скасовано')
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Готівка'),
        ('card', 'Картка'),
        ('transfer', 'Переказ')
    ]

    user_id = orm.ReferenceField(User, required=True)
    employee_id = orm.ReferenceField(Employee, required=True)
    products = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, price}]
    total_amount = orm.FloatField(required=True)
    sale_date = orm.DateTimeField(required=True)
    status = orm.StringField(required=True, choices=STATUS_CHOICES, default='paid')  # paid, pending, cancelled
    payment_method = orm.StringField(required=True, choices=PAYMENT_METHOD_CHOICES, default='cash')
    custom_build_service = orm.EmbeddedField(CustomBuildConfig, default=None)
    software_service = orm.EmbeddedField(SoftwareServiceConfig, default=None)
    warranty_end_date = orm.DateTimeField()
    notes = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class Repair(orm.Model):
    """Модель ремонту"""
    _collection_name = 'repairs'

    TYPE_CHOICES = [
        ('paid', 'Платний ремонт'),
        ('warranty', 'Гарантійний ремонт'),
        ('software', 'Ремонт програмного забезпечення'),
    ]

    STATUS_CHOICES = [
        ('received', 'Прийнято'),
        ('diagnosed', 'Діагностовано'),
        ('repairing', 'Ремонтується'),
        ('completed', 'Завершено'),
        ('returned', 'Повернено клієнту'),
        ('cancelled', 'Скасовано')
    ]

    user_id = orm.ReferenceField(User, required=True)
    product_id = orm.ReferenceField(Product)
    employee_id = orm.ReferenceField(Employee, required=True)
    sale_id = orm.ReferenceField(Sale)  # Якщо ремонт за гарантією
    products_used = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, price}]
    description = orm.StringField(required=True)  # Опис проблеми
    repair_type = orm.StringField(required=True, choices=TYPE_CHOICES, default='paid')  # warranty, paid, software
    cost = orm.FloatField(default=0)
    status = orm.StringField(required=True, choices=STATUS_CHOICES, default='received')  # received, diagnosed, repairing, completed, returned, cancelled
    start_date = orm.DateTimeField(required=True)
    estimated_completion = orm.DateTimeField()
    completion_date = orm.DateTimeField()
    technician_id = orm.ReferenceField('Employee')
    notes = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()

