# apps/main/models.py

from re import S
import core.mongo_orm as orm
import bcrypt
from datetime import datetime


class User(orm.Model):
    """Модель користувача"""
    _collection_name = "users"
    
    ROLE_CHOICES = [
        ("user", "User"),
        ("operator", "Operator"),
        ("admin", "Admin"),
    ]
    
    username = orm.StringField(required=True, unique=True, min_length=3, max_length=50)
    password_hash = orm.StringField(required=True)  # ← Зберігаємо hash, не пароль!
    email = orm.EmailField(required=True, unique=True)
    role = orm.StringField(required=True, choices=ROLE_CHOICES, default="user")
    is_active = orm.BooleanField(default=True)
    created_at = orm.DateTimeField(auto_now_add=True, default=datetime.now)
    last_login = orm.DateTimeField()
    
    def set_password(self, raw_password):
        """Хешування пароля"""
        self.password_hash = bcrypt.hashpw(
            raw_password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, raw_password):
        """Перевірка пароля"""
        return bcrypt.checkpw(
            raw_password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def update_last_login(self):
        """Оновити час останнього входу"""
        self.last_login = datetime.now()
        self.save()
    
    def to_dict(self, serialize=True, include_password=False):
        """Серіалізація без пароля"""
        data = super().to_dict(serialize)
        
        # Видаляємо password_hash з відповіді (якщо не вказано явно)
        if not include_password and 'password_hash' in data:
            del data['password_hash']
        
        return data


class ProductCategory(orm.Model):
    """Модель категорії товару/комплектуючого"""
    _collection_name = "product_categories"

    name = orm.StringField(required=True, unique=True)
    slug = orm.StringField(required=True, unique=True)
    description = orm.StringField()
    image_url = orm.URLField(required=True, unique=True)
    # redirect_url = orm.URLField(required=True, unique=True)
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class ProductSpecification(orm.Model):
    """Модель специфікації товару/комплектуючого"""

    name = orm.StringField(required=True)
    slug = orm.StringField(required=True)
    value = orm.StringField(required=True)


class Product(orm.Model):
    """Модель товару/комплектуючого"""
    _collection_name = 'products'

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

    name = orm.StringField(required=True, max_length=200)
    description = orm.StringField()
    category = orm.StringField(required=True)
    product_type = orm.StringField(required=True, choices=PRODUCT_TYPE_CHOICES)
    manufacturer = orm.StringField(required=True, max_length=150)
    # model = orm.StringField(max_length=100)
    specifications = orm.ListField(orm.EmbeddedField(ProductSpecification), default=list)
    price = orm.FloatField(required=True, default=0.0)  # Додано default
    quantity_in_stock = orm.IntegerField(default=0)
    warranty_months = orm.IntegerField(default=12)
    image_url = orm.URLField(required=True, unique=True)
    # redirect_url = orm.URLField(required=True, unique=True)
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class ProductListItem(orm.Model):
    """Модель товарів у списку покупки"""

    product_id = orm.ReferenceField(Product, required=True)
    quantity = orm.IntegerField(required=True, min_value=1)
    unit_price = orm.FloatField(required=True, min_value=0.0)


class SoftwareService(orm.Model):
    """Модель послуги налаштування ПЗ"""

    STATUS_CHOICES = [
        ('scheduled', 'Заплановано'),
        ('in_progress', 'Виконується'),
        ('completed', 'Завершено'),
        ('cancelled', 'Скасовано')
    ]

    description = orm.StringField(required=True)
    software_list = orm.ListField(orm.StringField())
    date_scheduled = orm.DateTimeField(required=True)
    date_completed = orm.DateTimeField()
    cost = orm.FloatField(min_value=0, required=True)
    status = orm.StringField(choices=STATUS_CHOICES, default='scheduled')


class SoftwareServiceConfig(orm.Model):
    purchased = orm.BooleanField(default=False)
    data = orm.EmbeddedField(SoftwareService)
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class CustomBuild(orm.Model):
    """Модель кастомної збірки ПК"""

    STATUS_CHOICES = [
        ('ordered', 'Замовлено'),
        ('components_ready', 'Компоненти готові'),
        ('assembling', 'Збирається'),
        ('testing', 'Тестується'),
        ('completed', 'Завершено'),
        ('delivered', 'Передано клієнту')
    ]

    name = orm.StringField(max_length=200)
    products = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, purpose}]
    total_cost = orm.FloatField(min_value=0)
    assembly_date = orm.DateTimeField()
    completion_date = orm.DateTimeField()
    status = orm.StringField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    notes = orm.StringField()


class CustomBuildConfig(orm.Model):
    purchased = orm.BooleanField(default=False)
    data = orm.EmbeddedField(CustomBuild)
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()


class PasswordResetToken(orm.Model):
    """Модель токену для скидання пароля"""
    _collection_name = "password_reset_tokens"
    
    user_id = orm.ReferenceField(User, required=True)
    token = orm.StringField(required=True, unique=True)
    expires_at = orm.DateTimeField(required=True)
    used = orm.BooleanField(default=False)
    created_at = orm.DateTimeField(default=datetime.now)
    
    @classmethod
    def create_token(cls, user):
        """Створити новий токен для користувача"""
        import secrets
        from datetime import timedelta
        
        # Генеруємо унікальний токен
        token = secrets.token_urlsafe(32)
        
        # Видаляємо старі невикористані токени для цього користувача
        try:
            old_tokens = cls.objects(user_id=user.id, used=False).all()
            for old_token in old_tokens:
                old_token.delete()
        except:
            pass  # Якщо помилка, продовжуємо
        
        # Створюємо новий токен (дійсний 1 годину)
        reset_token = cls(
            user_id=user.id,
            token=token,
            expires_at=datetime.now() + timedelta(hours=1),
            used=False
        )
        reset_token.save()
        
        return reset_token
    
    @classmethod
    def validate_token(cls, token):
        """Перевірити токен та повернути користувача"""
        try:
            reset_token = cls.objects(token=token, used=False).first()
            
            if not reset_token:
                return None
            
            if datetime.now() > reset_token.expires_at:
                # Токен прострочений
                return None
            
            # Повертаємо користувача (user_id - це ReferenceField, який повертає User об'єкт)
            return reset_token.user_id
        except Exception as e:
            print(f"Error validating token: {e}")
            return None
    
    def mark_as_used(self):
        """Позначити токен як використаний"""
        self.used = True
        self.save()


class Delivery(orm.Model):
    """Модель доставок"""
    _collection_name = "deliveries"

    STATUS_CHOICES = [
        ('ordered', 'Замовлено'),
        ('delivered', 'Доставлено'),
        ('received', 'Отримано'),
        ('cancelled', 'Повернено')
    ]

    sale_id = orm.ReferenceField('Sale', required=True)  # Reference to Sale
    user_id = orm.ReferenceField(User, required=True)  # Auto-filled from sale
    delivery_address = orm.StringField(required=True)  # Delivery address
    products = orm.ListField(orm.EmbeddedField(ProductListItem))  # [{product_id, quantity, unit_price}]
    total_cost = orm.FloatField(min_value=0)  # Delivery cost (not order total)
    delivery_date = orm.DateTimeField(required=True, default=datetime.now)
    received_date = orm.DateTimeField()
    status = orm.StringField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    notes = orm.StringField()
    created_at = orm.DateTimeField(default=datetime.now)
    updated_at = orm.DateTimeField(default=datetime.now)

    def update_updated_at(self):
        """Оновити час останнього оновлення"""
        self.updated_at = datetime.now()
        self.save()