from rest_framework import serializers
from apps.crm.serializers.product_list_item_serializer import ProductListItemSerializer
from apps.crm.models import Supply, Contract, Supplier, Product
from bson import ObjectId
from datetime import datetime

# === Supply serializer ===
class SupplySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)

    contract_id = serializers.CharField()
    supplier_id = serializers.CharField()
    products = ProductListItemSerializer(many=True)
    total_cost = serializers.FloatField()
    delivery_date = serializers.DateTimeField()
    received_date = serializers.DateTimeField()
    status = serializers.CharField()
    notes = serializers.CharField()
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # --------------------------
    # REPRESENTATION
    # --------------------------

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "contract": Contract.find_by_id(instance.contract_id).to_dict() if Contract.find_by_id(instance.contract_id) else str(instance.contract_id),
            "supplier": Supplier.find_by_id(instance.supplier_id).to_dict() if Supplier.find_by_id(instance.supplier_id) else str(instance.supplier_id),    

            "products": [
                {
                    "product": Product.find_by_id(item["product_id"]).to_dict() if Product.find_by_id(item["product_id"]) else None,
                    "product_id": str(item["product_id"]),
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "subtotal": round(float(item.get("quantity", 0)) * float(item.get("unit_price", 0)), 2),
                }
                for item in instance.products
            ],

            "total_cost": instance.total_cost,
            "delivery_date": instance.delivery_date,
            "received_date": instance.received_date,
            "status": instance.status,
            "notes": instance.notes,

            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }
