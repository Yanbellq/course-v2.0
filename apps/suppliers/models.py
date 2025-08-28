# apps/suppliers/models.py
from mongoengine import Document, StringField, EmailField, DateTimeField, ObjectIdField
from bson import ObjectId
import datetime

class Supplier(Document):
    # Використовуємо ObjectIdField для _id, mongoengine впорається з цим автоматично.
    id = StringField(primary_key=True, default=lambda: 'SUPP-' + str(ObjectId()))
    name = StringField(required=True, max_length=200)
    contact_person = StringField(max_length=200)
    phone = StringField(required=True, max_length=20)
    email = EmailField(required=True, unique=True)
    address = StringField()
    created_at = DateTimeField(default=datetime.datetime.utcnow)

    meta = {
        'collection': 'suppliers',
        'auto_create_index': False, # Важливо для MongoDB Atlas
        'indexes': [
            'name',
            'email'
        ]
    }

    def to_json_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "email": self.email,
            "address": self.address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }