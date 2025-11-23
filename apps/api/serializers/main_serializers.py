from rest_framework import serializers
from apps.main.models import Product, ProductCategory, ProductListItem


class ProductCategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    name = serializers.CharField(required=True, max_length=100)
    slug = serializers.CharField(required=True, max_length=100)
    description = serializers.CharField(allow_blank=True, required=False)
    image_url = serializers.URLField(required=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_name(self, value):
        # from apps.main.models import ProductCategory

        instance = getattr(self, "instance", None)
        # Перевірка на унікальність категорії (крім own update)
        query = ProductCategory.objects().filter(name=value)
        if instance:
            query = query.filter(_id__ne=instance.id)
        if query.first():
            raise serializers.ValidationError("Категорія з такою назвою вже існує")
        return value

    def validate_slug(self, value):
        # from apps.main.models import ProductCategory

        instance = getattr(self, "instance", None)
        # Перевірка на унікальність категорії (крім own update)
        query = ProductCategory.objects().filter(slug=value)
        if instance:
            query = query.filter(_id__ne=instance.id)
        if query.first():
            raise serializers.ValidationError("Категорія з таким slug вже існує")
        return value

    def validate_image_url(self, value):
        # from apps.main.models import ProductCategory

        instance = getattr(self, "instance", None)
        query = ProductCategory.objects().filter(image_url=value)
        if instance:
            query = query.filter(_id__ne=instance.id)
        if query.first():
            raise serializers.ValidationError(
                "Ця картинка вже прив'язана до іншої категорії"
            )
        return value

    def create(self, validated_data):
        # from apps.main.models import ProductCategory

        return ProductCategory.create(**validated_data)

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.update_updated_at()
        return instance


class ProductSpecificationSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    value = serializers.CharField()


class ProductSerializer(serializers.Serializer):
    """Серіалізатор для створення продукту"""

    COMPONENT_CHOICES = [
        ('cpu', 'Процесор'),
        ('motherboard', 'Материнська плата'),
        ('ram', 'Оперативна пам\'ять'),
        ('hdd', 'Жорсткий диск HDD'),
        ('ssd', 'Жорсткий диск SSD'),
        ('gpu', 'Відеокарта'),
        ('psu', 'Блок живлення'),
        ('sound_card', 'Звукова карта'),
        ('network_card', 'Мережева карта'),
        ('case', 'Корпус'),
    ]

    PERIPHERIAL_CHOICES = [
        ('monitor', 'Монітор'),
        ('keyboard', 'Клавіатура'),
        ('mouse', 'Миша'),
        ('headphone', 'Навушники'),
        ('printer', 'Принтер'),
        ('scanner', 'Сканер'),
    ]

    CAMERA_CHOICES = [
        ('webcam', 'Веб-камера'),
        ('camera', 'Камера'),
    ]

    PRODUCT_TYPE_CHOICES = COMPONENT_CHOICES + PERIPHERIAL_CHOICES + CAMERA_CHOICES + [
        ('laptop', 'Ноутбук'),
        ('smartphone', 'Смартфон'),
        ('smart-watch', 'Смарт-годинник'),
        ('other', 'Інше'),
    ]

    name = serializers.CharField(min_length=3, max_length=200, required=True)
    description = serializers.CharField(allow_blank=True, required=False, default="")
    category = serializers.CharField(min_length=2, max_length=100, required=True)
    product_type = serializers.ChoiceField(choices=PRODUCT_TYPE_CHOICES, required=True)
    manufacturer = serializers.CharField(max_length=150, allow_blank=True, required=True)
    specifications = serializers.ListSerializer(
        child=ProductSpecificationSerializer(),
        required=False,
        default=list,
        allow_empty=True
    )
    price = serializers.FloatField(min_value=0, max_value=10000000, required=True)
    quantity_in_stock = serializers.IntegerField(min_value=0, max_value=1000000, default=0, required=False)
    warranty_months = serializers.IntegerField(min_value=0, max_value=120, default=12, required=False)
    image_url = serializers.URLField(required=True)

    def validate_name(self, value):
        """Перевірка назви продукту"""
        if not value or not value.strip():
            raise serializers.ValidationError("Назва продукту не може бути порожньою")
        return value.strip()

    def validate_category(self, value):
        """Перевірка категорії"""
        if not value or not value.strip():
            raise serializers.ValidationError("Категорія не може бути порожньою")
        return value.strip()

    def validate_image_url(self, value):
        """Перевірка унікальності URL зображення"""
        existing_product = Product.objects().filter(image_url=value).first()
        if existing_product:
            raise serializers.ValidationError(
                "Продукт з таким URL зображення вже існує"
            )
        return value

    def validate_price(self, value):
        """Перевірка ціни"""
        if round(value, 2) != value:
            raise serializers.ValidationError(
                "Ціна може мати максимум 2 знаки після коми"
            )
        return value

    def validate_manufacturer(self, value):
        """Валідація виробника"""
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Назва виробника занадто коротка (мінімум 2 символи)"
            )
        return value.strip() if value else ""

    def create(self, validated_data):
        """Створення продукту"""
        product = Product(**validated_data)
        product.save()
        return product
    
    def update(self, instance, validated_data):
        """Оновлення продукту"""
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        instance.update_updated_at()
        return instance


class ProductViewSerializer(serializers.Serializer):
    """Серіалізатор для відображення продукту"""

    id = serializers.CharField(read_only=True)
    name = serializers.CharField()
    description = serializers.CharField()
    category = serializers.CharField()
    product_type = serializers.CharField()
    manufacturer = serializers.CharField()
    specifications = serializers.SerializerMethodField()
    price = serializers.FloatField()
    quantity_in_stock = serializers.IntegerField()
    warranty_months = serializers.IntegerField()
    image_url = serializers.URLField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    
    def get_specifications(self, obj):
        """Безпечна серіалізація specifications з обробкою різних форматів"""
        specs = getattr(obj, 'specifications', None) or []
        normalized_specs = []
        
        for spec in specs:
            if isinstance(spec, dict):
                # Якщо це словник, перевіряємо наявність потрібних полів
                if 'name' in spec and 'slug' in spec and 'value' in spec:
                    normalized_specs.append({
                        'name': spec.get('name', ''),
                        'slug': spec.get('slug', ''),
                        'value': spec.get('value', '')
                    })
            elif hasattr(spec, 'name') and hasattr(spec, 'slug') and hasattr(spec, 'value'):
                # Якщо це об'єкт з атрибутами
                normalized_specs.append({
                    'name': getattr(spec, 'name', ''),
                    'slug': getattr(spec, 'slug', ''),
                    'value': getattr(spec, 'value', '')
                })
            # Ігноруємо рядки та інші невідповідні типи
        
        return normalized_specs

    def to_representation(self, instance):
        """Додаткове форматування даних"""
        data = super().to_representation(instance)

        # Додаємо читабельну назву типу продукту
        product_type_choices_ua = {
            "cpu": "Процесор",
            "motherboard": "Материнська плата",
            "ram": "Оперативна пам'ять",
            "hdd": "Жорсткий диск",
            "ssd": "SSD",
            "gpu": "Відеокарта",
            "sound_card": "Звукова карта",
            "network_card": "Мережева карта",
            "psu": "Блок живлення",
            "case": "Корпус",
            "monitor": "Монітор",
            "keyboard": "Клавіатура",
            "mouse": "Миша",
            "printer": "Принтер",
            "scanner": "Сканер",
            "webcam": "Веб-камера",
            "laptop": "Ноутбук",
            "smartphone": "Смартфон",
            "headphone": "Навушники",
            "camera": "Камера",
            "smart-watch": "Смарт-годинник",
            "other": "Інше",
        }
        
        # Додаємо читабельну назву типу продукту
        # Пошук категорії за slug
        category_slug = data.get("category")
        if category_slug:
            category_obj = ProductCategory.objects().filter(slug=category_slug).first()
            if category_obj:
                data["category_name_en"] = category_obj.name
            else:
                data["category_name_en"] = category_slug

        product_type_choices_en = {
            "cpu": "Processor",
            "motherboard": "Motherboard",
            "ram": "RAM",
            "hdd": "Hard Disk HDD",
            "ssd": "Hard Disk SSD",
            "gpu": "Graphic Card",
            "sound_card": "Sound Card",
            "network_card": "Network Card",
            "psu": "PSU",
            "case": "Case",
            "monitor": "Monitor",
            "keyboard": "Keyboard",
            "mouse": "Mouse",
            "printer": "Printer",
            "scanner": "Scanner",
            "webcam": "Web-Camera",
            "laptop": "Laptop",
            "smartphone": "Smartphone",
            "headphone": "Headphones",
            "camera": "Camera",
            "smart-watch": "Smart Watch",
            "other": "Other",
        }

        product_type = data.get("product_type")
        if product_type:
            data["product_type_ua"] = product_type_choices_ua.get( product_type, product_type )
            data["product_type_en"] = product_type_choices_en.get( product_type, product_type )

        # Форматуємо ціну
        if data.get("price") is not None:
            data["price"] = round(data["price"], 2)

        return data
