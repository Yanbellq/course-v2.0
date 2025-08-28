from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.suppliers.models import Supplier


# Договори
class Contract(Document):
    number = fields.StringField(max_length=50, required=True, unique=True)
    supplier = fields.ReferenceField(Supplier, required=True)
    date_signed = fields.DateTimeField(required=True)
    delivery_date = fields.DateTimeField(required=True)
    total_amount = fields.DecimalField(min_value=0, precision=2)
    products = fields.ListField(fields.DictField())  # [{product_id, quantity, unit_price}]
    status = fields.StringField(max_length=20, choices=[
        ('active', 'Активний'),
        ('completed', 'Виконано'),
        ('cancelled', 'Скасовано')
    ], default='active')
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'contracts',
        'indexes': ['number', 'supplier', 'date_signed']
    }


