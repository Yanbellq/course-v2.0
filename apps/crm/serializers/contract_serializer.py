from rest_framework import serializers
from apps.crm.models import Contract, Supplier, Product
from apps.crm.serializers.product_list_item_serializer import ProductListItemSerializer
from bson import ObjectId
from datetime import datetime


# === Contract serializer ===
class ContractSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)

    number = serializers.CharField(max_length=8, required=False)
    supplier_id = serializers.CharField()
    total_amount = serializers.FloatField(required=False)
    signing_date = serializers.DateTimeField(required=False)
    status = serializers.CharField(default="active")
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    products = ProductListItemSerializer(many=True)

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # --------------------------
    # FIELD VALIDATION
    # --------------------------

    def validate_supplier_id(self, value):
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid supplier_id")

        supplier = Supplier.find_by_id(value)
        if not supplier:
            raise serializers.ValidationError("Supplier does not exist")

        return value

    def validate_status(self, value):
        valid = [c[0] for c in Contract.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError("Invalid contract status")
        return value

    # --------------------------
    # OBJECT VALIDATION
    # --------------------------

    def validate(self, data):
        """Auto-calc total_amount if missing."""
        products = data.get("products", [])

        if products:
            data["total_amount"] = sum([
                item["unit_price"] * item["quantity"]
                for item in products
            ])

        return data

    # --------------------------
    # CREATE
    # --------------------------

    # def create(self, validated_data):
    #     return Contract.create(**validated_data)
    def create(self, validated_data):
        if not validated_data.get("number"):
            validated_data["number"] = Contract.generate_unique_number()
        return Contract.create(**validated_data)

    # --------------------------
    # UPDATE
    # --------------------------

    def update(self, instance, validated_data):
        instance.number = validated_data.get("number", instance.number)
        instance.supplier_id = ObjectId(validated_data.get("supplier_id", instance.supplier_id))
        instance.status = validated_data.get("status", instance.status)
        instance.notes = validated_data.get("notes", instance.notes)

        # Dates
        if "signing_date" in validated_data:
            instance.signing_date = validated_data["signing_date"]

        # Products list
        if "products" in validated_data:
            instance.products = validated_data["products"]

        # Auto recalc total
        if "products" in validated_data:
            instance.total_amount = sum(
                item["unit_price"] * item["quantity"]
                for item in validated_data["products"]
            )

        # instance.updated_at = datetime.now()
        instance.save()
        instance.update_updated_at()

        return instance

    # --------------------------
    # REPRESENTATION
    # --------------------------

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "number": instance.number,
            # "supplier": instance.supplier_id.to_dict() if hasattr(instance.supplier_id, "to_dict") else str(instance.supplier_id),
            "supplier_id": str(instance.supplier_id),
            "supplier": Supplier.find_by_id(instance.supplier_id).to_dict() if Supplier.find_by_id(instance.supplier_id) else str(instance.supplier_id),    
            "total_amount": instance.total_amount,
            "signing_date": instance.signing_date,
            "status": instance.status,
            "notes": instance.notes,

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

            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }

