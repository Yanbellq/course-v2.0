from rest_framework import serializers
from apps.crm.serializers.product_list_item_serializer import ProductListItemSerializer
from apps.crm.serializers.sale_serializer import SaleSerializer
from apps.main.models import Delivery, User
from apps.crm.models import Sale, Product
from bson import ObjectId
from datetime import datetime
from django.utils import timezone as django_timezone

# === Delivery serializer ===
class DeliverySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)

    sale_id = serializers.CharField()
    user_id = serializers.CharField()
    delivery_address = serializers.CharField(required=True)
    products = ProductListItemSerializer(many=True)
    total_cost = serializers.FloatField()  # Delivery cost (manually entered)
    delivery_date = serializers.DateTimeField()
    received_date = serializers.DateTimeField(required=False, allow_null=True)
    status = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    
    def to_internal_value(self, data):
        """Override to prevent timezone conversion of naive datetime"""
        # Get the raw data first
        ret = super().to_internal_value(data)
        
        # If delivery_date is timezone-aware, convert to naive preserving the date/time
        if 'delivery_date' in ret and ret['delivery_date']:
            dt = ret['delivery_date']
            if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
                # Convert to local timezone first, then extract components
                local_tz = django_timezone.get_current_timezone()
                local_dt = dt.astimezone(local_tz)
                # Create naive datetime with local date/time components
                ret['delivery_date'] = datetime(
                    local_dt.year, local_dt.month, local_dt.day,
                    local_dt.hour, local_dt.minute, local_dt.second, local_dt.microsecond
                )
        
        return ret
    
    def validate_delivery_date(self, value):
        """Ensure delivery_date is stored as naive datetime without timezone conversion"""
        if value:
            # If timezone-aware, convert to naive by extracting date/time components
            # This preserves the exact date/time without timezone conversion
            if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                # Convert to local timezone first, then extract components
                local_tz = django_timezone.get_current_timezone()
                local_dt = value.astimezone(local_tz)
                # Create new naive datetime with local date/time components (no timezone conversion)
                # This prevents date shifting when converting from UTC
                value = datetime(
                    local_dt.year, local_dt.month, local_dt.day,
                    local_dt.hour, local_dt.minute, local_dt.second, local_dt.microsecond
                )
            # Keep the time as is (don't force to midnight)
        return value
    
    def validate_received_date(self, value):
        """Ensure received_date is stored as naive datetime at midnight"""
        if value:
            # If timezone-aware, convert to naive (remove timezone info)
            if hasattr(value, 'tzinfo') and value.tzinfo is not None:
                # Get the date part only, ignoring timezone conversion
                value = datetime(value.year, value.month, value.day, 0, 0, 0, 0)
            else:
                # Ensure time is set to midnight
                value = value.replace(hour=0, minute=0, second=0, microsecond=0)
        return value
    
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    # --------------------------
    # FIELD VALIDATION
    # --------------------------

    def validate_sale_id(self, value):
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid sale_id")
        
        sale = Sale.find_by_id(value)
        if not sale:
            raise serializers.ValidationError("Sale does not exist")
        
        return value

    def validate_user_id(self, value):
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid user_id")
        
        user = User.find_by_id(value)
        if not user:
            raise serializers.ValidationError("User does not exist")
        
        return value

    def validate_status(self, value):
        valid = [c[0] for c in Delivery.STATUS_CHOICES]
        if value not in valid:
            raise serializers.ValidationError("Invalid delivery status")
        return value

    # --------------------------
    # OBJECT VALIDATION
    # --------------------------

    def validate(self, data):
        """Validate delivery data."""
        # total_cost is delivery cost, not order total - entered manually
        # No auto-calculation needed
        return data

    # --------------------------
    # CREATE
    # --------------------------

    def create(self, validated_data):
        return Delivery.create(**validated_data)

    # --------------------------
    # UPDATE
    # --------------------------

    def update(self, instance, validated_data):
        instance.sale_id = ObjectId(validated_data.get("sale_id", instance.sale_id))
        instance.user_id = ObjectId(validated_data.get("user_id", instance.user_id))
        instance.delivery_address = validated_data.get("delivery_address", instance.delivery_address)
        instance.status = validated_data.get("status", instance.status)
        instance.notes = validated_data.get("notes", instance.notes)
        instance.delivery_date = validated_data.get("delivery_date", instance.delivery_date)
        instance.received_date = validated_data.get("received_date", instance.received_date)
        instance.total_cost = validated_data.get("total_cost", instance.total_cost)  # Delivery cost (manual)

        # Products list
        if "products" in validated_data:
            instance.products = validated_data["products"]

        instance.updated_at = datetime.now()
        instance.save()
        instance.update_updated_at()

        return instance

    # --------------------------
    # REPRESENTATION
    # --------------------------

    def to_representation(self, instance):
        sale = Sale.find_by_id(instance.sale_id) if instance.sale_id else None
        user = User.find_by_id(instance.user_id) if instance.user_id else None
        
        # Use SaleSerializer to get full sale data including custom_build_service and software_service
        sale_data = SaleSerializer(sale).data if sale else None
        
        return {
            "id": str(instance.id),
            "sale": sale_data,  # Full sale data with custom_build_service and software_service
            "sale_id": str(instance.sale_id) if instance.sale_id else None,
            "user": user.to_dict() if user else None,
            "user_id": str(instance.user_id) if instance.user_id else None,
            "delivery_address": instance.delivery_address if hasattr(instance, 'delivery_address') else None,
            
            "products": [
                {
                    "product": Product.find_by_id(item["product_id"]).to_dict() if Product.find_by_id(item["product_id"]) else None,
                    "product_id": str(item["product_id"]),
                    "quantity": item["quantity"],
                    "unit_price": item["unit_price"],
                    "subtotal": round(float(item.get("quantity", 0)) * float(item.get("unit_price", 0)), 2),
                }
                for item in (instance.products if instance.products else [])
            ],

            "total_cost": instance.total_cost,
            "delivery_date": instance.delivery_date,
            "received_date": instance.received_date,
            "status": instance.status,
            "notes": instance.notes,

            "created_at": instance.created_at,
            "updated_at": instance.updated_at,
        }

