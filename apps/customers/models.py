# Модель клієнта

from bson import ObjectId
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

# Клієнти
class Customer(Document):
    id = fields.StringField(primary_key=True, unique=True, default=lambda: 'CUST-' + str(ObjectId()))
    name = fields.StringField(required=True)
    surname = fields.StringField(required=True)
    phone = fields.StringField(required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    address = fields.StringField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'customers',

        'auto_create_index': False,
        'indexes': [
            'email',
            'phone',
        ]
    }


