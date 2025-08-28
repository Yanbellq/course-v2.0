from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

from apps.customers.models import Customer
from apps.products.models import Product
from apps.sales.models import Sale


# Гарантії
class Warranty(Document):
    sale = fields.ReferenceField(Sale, required=True)
    product = fields.ReferenceField(Product, required=True)
    customer = fields.ReferenceField(Customer, required=True)
    start_date = fields.DateTimeField(required=True)
    end_date = fields.DateTimeField(required=True)
    warranty_months = fields.IntField(required=True)
    is_active = fields.BooleanField(default=True)

    meta = {
        'collection': 'warranties',
        'indexes': ['sale', 'product', 'customer', 'end_date']
    }

