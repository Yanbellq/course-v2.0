from rest_framework import serializers
from apps.main.models import User

class UserRegistrationSerializer(serializers.Serializer):
    """Серіалізатор для реєстрації"""
    username = serializers.CharField(
        min_length=3, 
        max_length=50,
        required=True
    )
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        min_length=6, 
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        min_length=6,
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    role = serializers.ChoiceField(
        choices=['user', 'admin'],
        default='user'
    )
    
    def validate_username(self, value):
        """Перевірка унікальності username"""
        existing_user = User.objects().filter(username=value).first()
        if existing_user:
            raise serializers.ValidationError("Користувач з таким username вже існує")
        return value
    
    def validate_email(self, value):
        """Перевірка унікальності email"""
        existing_user = User.objects().filter(email=value).first()
        if existing_user:
            raise serializers.ValidationError("Користувач з таким email вже існує")
        return value
    
    def validate(self, data):
        """Перевірка збігу паролів"""
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({
                "password_confirm": "Паролі не співпадають"
            })
        return data
    
    def create(self, validated_data):
        """Створення користувача"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Серіалізатор для входу"""
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, data):
        """Валідація логіна і пароля"""
        username = data.get('username')
        password = data.get('password')
        
        # Знаходимо користувача
        user = User.objects().filter(username=username).first()
        
        if not user:
            raise serializers.ValidationError({
                "username": "Користувача з таким username не знайдено"
            })
        
        # Перевіряємо пароль
        if not user.check_password(password):
            raise serializers.ValidationError({
                "password": "Невірний пароль"
            })
        
        # Перевіряємо чи активний користувач
        if not user.is_active:
            raise serializers.ValidationError({
                "non_field_errors": "Обліковий запис деактивовано"
            })
        
        data['user'] = user
        return data


class UserSerializer(serializers.Serializer):
    """Серіалізатор для відображення користувача"""
    id = serializers.CharField(read_only=True)
    username = serializers.CharField()
    email = serializers.EmailField()
    role = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
