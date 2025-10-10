# Модель клієнта

from bson import ObjectId
from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

# Клієнти
class Customer(Document):
    id = fields.StringField(primary_key=True, default=lambda: 'CUST-' + str(ObjectId()))
    username = fields.StringField(required=True)
    email = fields.EmailField(required=True)
    password = fields.StringField(required=True)

    token = fields.StringField(required=False, blank=True, default=None)

    address = fields.StringField(required=False, blank=True, default=None)
    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'customers',
        'indexes': [
            # {'fields': ['id'], 'unique': True},
            {'fields': ['username'], 'unique': True},
            {'fields': ['email'], 'unique': True},
            {'fields': ['token'], 'unique': True, 'sparse': True}
        ],
        'index_background': False  # This is the proper way to set background indexing
    }



class Admin(Document):
    id = fields.StringField(primary_key=True, default=lambda: 'ADMIN-' + str(ObjectId()))
    email = fields.EmailField(required=True)
    password = fields.StringField(required=True)

    token = fields.StringField(required=False, blank=True, default=None)

    created_at = fields.DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'admins',
        'indexes': [
            # {'fields': ['id'], 'unique': True},
            {'fields': ['email'], 'unique': True},
            {'fields': ['token'], 'unique': True, 'sparse': True}
        ],
        'index_background': False  # This is the proper way to set background indexing
    }