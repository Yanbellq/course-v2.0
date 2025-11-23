from rest_framework import serializers
from apps.crm.models import Product
from bson import ObjectId
from datetime import datetime

# === ProductListItem serializer ===
class ProductListItemSerializer(serializers.Serializer):
    product_id = serializers.CharField()
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.FloatField(min_value=0)

    def validate_product_id(self, value):
        if not ObjectId.is_valid(value):
            raise serializers.ValidationError("Invalid product_id")

        product = Product.find_by_id(value)
        if not product:
            raise serializers.ValidationError("Product does not exist")

        return value

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        value["product_id"] = ObjectId(value["product_id"])
        return value