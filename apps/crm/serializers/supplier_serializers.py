from rest_framework import serializers
from apps.crm.models import Supplier

class SupplierSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(max_length=255)
    contact_person = serializers.CharField(max_length=255, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(max_length=50, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_email(self, value):
        """Перевірка унікальності email"""
        if not value:
            return value
        
        # Отримуємо instance для редагування (якщо є)
        instance = self.instance
        
        # Перевіряємо чи існує інший supplier з таким email
        existing = Supplier.objects().filter(email=value).first()
        if existing and (not instance or str(existing.id) != str(instance.id)):
            raise serializers.ValidationError("Supplier with this email already exists.")
        return value

    def validate_phone(self, value):
        """Перевірка унікальності phone"""
        if not value:
            return value
        
        # Отримуємо instance для редагування (якщо є)
        instance = self.instance
        
        # Перевіряємо чи існує інший supplier з таким phone
        existing = Supplier.objects().filter(phone=value).first()
        if existing and (not instance or str(existing.id) != str(instance.id)):
            raise serializers.ValidationError("Supplier with this phone number already exists.")
        return value

    def create(self, validated_data):
        return Supplier.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.update_updated_at()
        return instance

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "name": instance.name,
            "contact_person": instance.contact_person,
            "email": instance.email,
            "phone": instance.phone,
            "address": instance.address,
            "description": instance.description,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }