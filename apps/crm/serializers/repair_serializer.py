from rest_framework import serializers
from apps.crm.serializers.product_list_item_serializer import ProductListItemSerializer
from apps.crm.models import Sale, Supply, Contract, Supplier, Product, Employee
from apps.main.models import User, SoftwareServiceConfig, CustomBuildConfig
from bson import ObjectId
from datetime import datetime

# === Repair serializer ===
class RepairSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField()
    product_id = serializers.CharField()
    products_used = ProductListItemSerializer(many=True)
    employee_id = serializers.CharField()
    description = serializers.CharField()
    repair_type = serializers.CharField()
    status = serializers.CharField()
    cost = serializers.FloatField()
    start_date = serializers.DateTimeField()
    estimated_completion = serializers.DateTimeField()
    completion_date = serializers.DateTimeField()
    technician_id = serializers.CharField()
    notes = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "user": User.find_by_id(instance.user_id).to_dict() if User.find_by_id(instance.user_id) else str(instance.user_id),
            "product": Product.find_by_id(instance.product_id).to_dict() if Product.find_by_id(instance.product_id) else str(instance.product_id),
            
            "products_used": [
                {
                    "product": (Product.find_by_id(item.get("product_id")).to_dict() if Product.find_by_id(item.get("product_id")) else None) if item.get("product_id") else None,
                    "product_id": str(item.get("product_id", "")),
                    "quantity": item.get("quantity", 0),
                    "unit_price": item.get("unit_price", 0),
                    "subtotal": round(float(item.get("quantity", 0)) * float(item.get("unit_price", 0)), 2),
                }
                for item in (instance.products_used or [])
            ],

            "employee": Employee.find_by_id(instance.employee_id).to_dict() if Employee.find_by_id(instance.employee_id) else str(instance.employee_id),
            "description": instance.description,
            "repair_type": instance.repair_type,
            "status": instance.status,
            "cost": instance.cost,
            "start_date": instance.start_date,
            "estimated_completion": instance.estimated_completion,
            "completion_date": instance.completion_date,
            "technician_id": str(instance.technician_id),
            "notes": instance.notes,
            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }