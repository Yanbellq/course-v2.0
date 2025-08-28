from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime

# Співробітники
class Employee(Document):
    first_name = fields.StringField(max_length=50, required=True)
    last_name = fields.StringField(max_length=50, required=True)
    position = fields.StringField(max_length=100, required=True)
    phone = fields.StringField(max_length=20)
    email = fields.EmailField()
    hire_date = fields.DateTimeField(required=True)
    salary = fields.DecimalField(min_value=0, precision=2)
    is_active = fields.BooleanField(default=True)

    meta = {
        'collection': 'employees',
        'indexes': ['last_name', 'position']
    }