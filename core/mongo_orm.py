from bson import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Optional
from core.mongo_connection import get_db


# ==================== БАЗОВІ КЛАСИ ПОЛІВ ====================

class Field:
    """Базовий клас для полів моделі"""
    
    def __init__(self, required=False, default=None, unique=False, 
                 choices=None, validators=None, help_text=''):
        self.required = required
        self.default = default
        self.unique = unique
        self.choices = choices  # НОВЕ (опціонально)
        self.validators = validators or []  # НОВЕ (опціонально)
        self.help_text = help_text  # НОВЕ (опціонально)
    
    def validate(self, value):
        """Валідація значення"""
        # СТАРИЙ КОД
        if self.required and value is None:
            raise ValueError(f"Поле є обов'язковим")
        
        # НОВИЙ КОД - choices
        if value is not None and self.choices:
            valid_choices = [choice[0] if isinstance(choice, tuple) else choice 
                           for choice in self.choices]
            if value not in valid_choices:
                raise ValueError(f"Значення має бути одним з: {valid_choices}")
        
        # НОВИЙ КОД - кастомні валідатори
        if value is not None and self.validators:
            for validator in self.validators:
                validator(value)
        
        return True
    
    def to_python(self, value):
        return value
    
    def to_mongo(self, value):
        return value
    
    def get_choices_display(self, value):
        """НОВИЙ МЕТОД - отримати відображення для choices"""
        if not self.choices:
            return value
        
        for choice in self.choices:
            if isinstance(choice, tuple):
                if choice[0] == value:
                    return choice[1]
            elif choice == value:
                return value
        return value


class StringField(Field):
    """Поле для рядків"""
    
    def __init__(self, max_length=None, min_length=None, regex=None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length
        self.min_length = min_length  # НОВЕ (опціонально)
        self.regex = regex  # НОВЕ (опціонально)
    
    def validate(self, value):
        super().validate(value)
        
        # СТАРИЙ КОД
        if value and not isinstance(value, str):
            raise ValueError("Значення має бути рядком")
        if self.max_length and value and len(value) > self.max_length:
            raise ValueError(f"Максимальна довжина {self.max_length}")
        
        # НОВИЙ КОД
        if self.min_length and value and len(value) < self.min_length:
            raise ValueError(f"Мінімальна довжина {self.min_length}")
        
        if self.regex and value:
            import re
            if not re.match(self.regex, value):
                raise ValueError(f"Значення не відповідає шаблону {self.regex}")
        
        return True


class IntegerField(Field):
    """Поле для цілих чисел"""
    
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value  # НОВЕ (опціонально)
        self.max_value = max_value  # НОВЕ (опціонально)
    
    def validate(self, value):
        super().validate(value)
        
        # СТАРИЙ КОД
        if value is not None and not isinstance(value, int):
            raise ValueError("Значення має бути цілим числом")
        
        # НОВИЙ КОД
        if self.min_value is not None and value is not None and value < self.min_value:
            raise ValueError(f"Мінімальне значення {self.min_value}")
        
        if self.max_value is not None and value is not None and value > self.max_value:
            raise ValueError(f"Максимальне значення {self.max_value}")
        
        return True


class FloatField(Field):
    """Поле для дробових чисел"""
    
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value  # НОВЕ (опціонально)
        self.max_value = max_value  # НОВЕ (опціонально)
    
    def validate(self, value):
        super().validate(value)
        
        # СТАРИЙ КОД
        if value is not None and not isinstance(value, (int, float)):
            raise ValueError("Значення має бути числом")
        
        # НОВИЙ КОД
        if self.min_value is not None and value is not None and value < self.min_value:
            raise ValueError(f"Мінімальне значення {self.min_value}")
        
        if self.max_value is not None and value is not None and value > self.max_value:
            raise ValueError(f"Максимальне значення {self.max_value}")
        
        return True
    
    def to_python(self, value):
        return float(value) if value is not None else None


class BooleanField(Field):
    """Поле для булевих значень"""
    
    def to_python(self, value):
        return bool(value) if value is not None else None


class DateTimeField(Field):
    """Поле для дати та часу"""
    
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
    
    def to_python(self, value):
        if isinstance(value, datetime):
            return value
        return value
    
    def to_mongo(self, value):
        if self.auto_now or (self.auto_now_add and value is None):
            return datetime.now()
        return value


class ListField(Field):
    """Поле для списків"""
    
    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, list):
            raise ValueError("Значення має бути списком")
        return True


class DictField(Field):
    """Поле для словників"""
    
    def validate(self, value):
        super().validate(value)
        if value is not None and not isinstance(value, dict):
            raise ValueError("Значення має бути словником")
        return True


class ReferenceField(Field):
    """Поле для зв'язків між колекціями"""
    
    def __init__(self, reference_to, **kwargs):
        super().__init__(**kwargs)
        self.reference_to = reference_to
    
    def validate(self, value):
        # Convert empty string to None for required fields
        if isinstance(value, str) and value.strip() == '':
            value = None
        
        # Call parent validation
        super().validate(value)
        return True
    
    def to_mongo(self, value):
        # Convert empty string to None
        if isinstance(value, str) and value.strip() == '':
            return None
        
        if value is None:
            return None
        
        if isinstance(value, ObjectId):
            return value
        if isinstance(value, str):
            return ObjectId(value)
        if hasattr(value, 'id'):  # ВИПРАВЛЕНО: було value.id тепер hasattr
            return value.id
        return value


class EmbeddedField(Field):
    def __init__(self, model_class, **kwargs):
        super().__init__(**kwargs)
        self.model_class = model_class

    def validate(self, value):
        # Якщо значення None і поле не обов'язкове, пропускаємо валідацію
        if value is None:
            if not self.required:
                return True
            else:
                raise ValueError(f"Поле є обов'язковим для {self.model_class.__name__}")
        
        # Перевірка що це словник або вже модель
        # Якщо це вже екземпляр моделі, конвертуємо в словник
        if not isinstance(value, dict):
            if hasattr(value, 'to_dict'):
                value = value.to_dict()
            else:
                # Якщо це об'єкт моделі, спробуємо отримати атрибути
                if isinstance(value, self.model_class):
                    # Це вже правильний тип, пропускаємо перетворення
                    return True
                raise ValueError(f"Значення має бути словником для {self.model_class.__name__}")

        # Спроба створити модель (оцінка валідності)
        try:
            model_instance = self.model_class(**value)
            # Викликаємо validate() тільки якщо метод існує
            if hasattr(model_instance, 'validate'):
                try:
                    model_instance.validate()
                except AttributeError:
                    # Ігноруємо якщо метод validate не працює
                    pass
        except AttributeError:
            # Ігноруємо помилки AttributeError (наприклад, якщо validate не існує)
            pass
        except Exception as e:
            # Тільки для інших помилок викидаємо ValueError
            raise ValueError(f"Невірні дані для {self.model_class.__name__}: {e}")

        return True

    def to_mongo(self, value):
        # Якщо значення None, повертаємо None
        if value is None:
            return None
        
        # Якщо це вже словник, повертаємо його
        if isinstance(value, dict):
            return value
        
        # Якщо це об'єкт моделі, конвертуємо в словник
        if isinstance(value, self.model_class):
            # Використовуємо to_dict якщо є, інакше створюємо словник з атрибутів
            if hasattr(value, 'to_dict'):
                return value.to_dict()
            else:
                # Створюємо словник з атрибутів моделі
                result = {}
                for field_name in self.model_class._fields.keys():
                    if hasattr(value, field_name):
                        field_value = getattr(value, field_name)
                        # Конвертуємо вложені об'єкти в словники
                        if hasattr(field_value, 'to_dict'):
                            result[field_name] = field_value.to_dict()
                        elif isinstance(field_value, (list, tuple)):
                            result[field_name] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in field_value]
                        else:
                            result[field_name] = field_value
                return result
        
        # Якщо є метод to_dict, використовуємо його
        if hasattr(value, 'to_dict'):
            return value.to_dict()
        
        raise ValueError(f"Некоректне значення для {self.model_class.__name__}")

    def to_python(self, value):
        # Повертаємо модель або словник
        if isinstance(value, dict):
            return self.model_class(**value)
        elif hasattr(value, 'to_dict'):
            return value
        else:
            return value
        

# ==================== НОВІ СПЕЦІАЛІЗОВАНІ ПОЛЯ ====================

class EmailField(StringField):
    """Поле для email з автоматичною валідацією"""
    
    def __init__(self, **kwargs):
        if 'regex' not in kwargs:
            kwargs['regex'] = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        super().__init__(**kwargs)


class URLField(StringField):
    """Поле для URL"""
    
    def __init__(self, **kwargs):
        if 'regex' not in kwargs:
            kwargs['regex'] = r'^https?://.*$'
        super().__init__(**kwargs)


class PhoneField(StringField):
    """Поле для телефону"""
    
    def __init__(self, **kwargs):
        if 'regex' not in kwargs:
            kwargs['regex'] = r'^\+?[\d\s\-()]+$'
        super().__init__(**kwargs)


# ==================== МЕТАКЛАС ====================

class ModelMeta(type):
    """Метаклас для моделей"""
    
    def __new__(mcs, name, bases, attrs):
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value
                attrs.pop(key)
        
        attrs['_fields'] = fields
        attrs['_collection_name'] = attrs.get('_collection_name', 
                                               name.lower() + 's')
        
        return super().__new__(mcs, name, bases, attrs)



class QuerySet:
    """Клас для роботи з запитами"""
    
    def __init__(self, model_class, collection):
        self.model_class = model_class
        self.collection = collection
        self._filter = {}
        self._sort = None
        self._limit_value = None
        self._skip_value = 0
    
    def filter(self, **kwargs):
        """
        Фільтрація документів з підтримкою операторів
        
        Приклади:
            .filter(age__gte=18)  # age >= 18
            .filter(name__in=['John', 'Jane'])
            .filter(price__lte=1000)
            .filter(name='Intel')  # звичайна фільтрація
        """
        query = QuerySet(self.model_class, self.collection)
        mongo_query = self._parse_filter_kwargs(kwargs)
        query._filter = {**self._filter, **mongo_query}
        query._sort = self._sort
        query._limit_value = self._limit_value
        query._skip_value = self._skip_value
        return query
    
    def _parse_filter_kwargs(self, kwargs):
        """Парсинг kwargs з операторами (ВИПРАВЛЕНО)"""
        mongo_query = {}
        
        for key, value in kwargs.items():
            # Розбираємо оператори типу field__gte, field__lte
            if '__' in key and not key.startswith('_'):
                parts = key.rsplit('__', 1)
                if len(parts) == 2:
                    field, operator = parts
                    
                    # Конвертуємо id в _id для MongoDB
                    if field == 'id':
                        field = '_id'
                        if isinstance(value, str):
                            value = ObjectId(value)
                    elif field.endswith('_id'):
                        if isinstance(value, str):
                            value = ObjectId(value)
                    
                    # Оператори порівняння
                    if operator == 'gte':  # greater than or equal
                        # ВИПРАВЛЕНО: Об'єднуємо з існуючими умовами
                        if field in mongo_query and isinstance(mongo_query[field], dict):
                            mongo_query[field]['$gte'] = value
                        else:
                            mongo_query[field] = {'$gte': value}
                            
                    elif operator == 'gt':  # greater than
                        if field in mongo_query and isinstance(mongo_query[field], dict):
                            mongo_query[field]['$gt'] = value
                        else:
                            mongo_query[field] = {'$gt': value}
                            
                    elif operator == 'lte':  # less than or equal
                        # ВИПРАВЛЕНО: Об'єднуємо з існуючими умовами
                        if field in mongo_query and isinstance(mongo_query[field], dict):
                            mongo_query[field]['$lte'] = value
                        else:
                            mongo_query[field] = {'$lte': value}
                            
                    elif operator == 'lt':  # less than
                        if field in mongo_query and isinstance(mongo_query[field], dict):
                            mongo_query[field]['$lt'] = value
                        else:
                            mongo_query[field] = {'$lt': value}
                            
                    elif operator == 'ne':  # not equal
                        mongo_query[field] = {'$ne': value}
                    elif operator == 'in':  # in list
                        mongo_query[field] = {'$in': value}
                    elif operator == 'nin':  # not in list
                        mongo_query[field] = {'$nin': value}
                    elif operator == 'contains':  # string contains
                        mongo_query[field] = {'$regex': value, '$options': 'i'}
                    elif operator == 'icontains':  # case-insensitive contains
                        mongo_query[field] = {'$regex': value, '$options': 'i'}
                    elif operator == 'startswith':  # string starts with
                        mongo_query[field] = {'$regex': f'^{value}', '$options': 'i'}
                    elif operator == 'endswith':  # string ends with
                        mongo_query[field] = {'$regex': f'{value}$', '$options': 'i'}
                    elif operator == 'exists':  # field exists
                        mongo_query[field] = {'$exists': value}
                    else:
                        # Якщо оператор невідомий, просто field = value
                        mongo_query[key] = value
                else:
                    # Якщо не вдалось розпарсити, залишаємо як є
                    mongo_query[key] = value
            else:
                # Звичайне порівняння
                if key == 'id':
                    mongo_query['_id'] = ObjectId(value) if isinstance(value, str) else value
                elif key.endswith('_id') and not key.startswith('_'):
                    mongo_query[key] = ObjectId(value) if isinstance(value, str) else value
                else:
                    mongo_query[key] = value
        
        return mongo_query

    
    def exclude(self, **kwargs):
        """Виключення документів (протилежність filter) - НОВИЙ МЕТОД"""
        mongo_query = self._parse_filter_kwargs(kwargs)
        
        query = QuerySet(self.model_class, self.collection)
        
        # Додаємо $not до кожного поля
        not_query = {}
        for key, value in mongo_query.items():
            if isinstance(value, dict) and any(k.startswith('$') for k in value.keys()):
                not_query[key] = {'$not': value}
            else:
                not_query[key] = {'$ne': value}
        
        query._filter = {**self._filter, **not_query}
        query._sort = self._sort
        query._limit_value = self._limit_value
        query._skip_value = self._skip_value
        return query
    
    def sort(self, field, direction=1):
        """Сортування (-1 DESC, 1 ASC) - СТАРИЙ МЕТОД"""
        query = QuerySet(self.model_class, self.collection)
        query._filter = self._filter
        query._sort = (field, direction)
        query._limit_value = self._limit_value
        query._skip_value = self._skip_value
        return query
    
    def order_by(self, *fields):
        """
        Сортування з підтримкою декількох полів - НОВИЙ МЕТОД
        
        Приклади:
            .order_by('name')           # сортування по name (ASC)
            .order_by('-price')         # сортування по price (DESC)
            .order_by('-price', 'name') # спочатку по price DESC, потім по name ASC
        """
        query = QuerySet(self.model_class, self.collection)
        query._filter = self._filter
        query._limit_value = self._limit_value
        query._skip_value = self._skip_value
        
        sort_list = []
        for field in fields:
            if field.startswith('-'):
                sort_list.append((field[1:], -1))
            else:
                sort_list.append((field, 1))
        
        query._sort = sort_list if len(sort_list) > 1 else sort_list[0] if sort_list else None
        return query
    
    def limit(self, limit):
        """Обмеження кількості результатів - СТАРИЙ МЕТОД"""
        query = QuerySet(self.model_class, self.collection)
        query._filter = self._filter
        query._sort = self._sort
        query._limit_value = limit
        query._skip_value = self._skip_value
        return query
    
    def skip(self, skip):
        """Пропустити N документів - СТАРИЙ МЕТОД"""
        query = QuerySet(self.model_class, self.collection)
        query._filter = self._filter
        query._sort = self._sort
        query._limit_value = self._limit_value
        query._skip_value = skip
        return query
    
    def count(self):
        """Підрахунок документів - СТАРИЙ МЕТОД"""
        return self.collection.count_documents(self._filter)
    
    def all(self):
        """Отримати всі документи - СТАРИЙ МЕТОД (оновлений для order_by)"""
        cursor = self.collection.find(self._filter)
        
        if self._sort:
            # Підтримка як старого sort(), так і нового order_by()
            if isinstance(self._sort, list):
                cursor = cursor.sort(self._sort)
            else:
                cursor = cursor.sort(*self._sort if isinstance(self._sort, tuple) else [self._sort])
        
        if self._skip_value:
            cursor = cursor.skip(self._skip_value)
        if self._limit_value:
            cursor = cursor.limit(self._limit_value)
        
        return [self.model_class(**doc) for doc in cursor]
    
    def first(self):
        """Отримати перший документ - СТАРИЙ МЕТОД"""
        doc = self.collection.find_one(self._filter)
        return self.model_class(**doc) if doc else None
    
    def get(self, **kwargs):
        """Отримати один документ за критеріями - СТАРИЙ МЕТОД"""
        mongo_kwargs = {}
        for key, value in kwargs.items():
            if key == 'id':
                mongo_kwargs['_id'] = ObjectId(value) if isinstance(value, str) else value
            else:
                mongo_kwargs[key] = value
        
        filter_query = {**self._filter, **mongo_kwargs}
        doc = self.collection.find_one(filter_query)
        if not doc:
            raise Exception(f"Документ не знайдено: {filter_query}")
        return self.model_class(**doc)
    
    def delete(self):
        """Видалити документи - СТАРИЙ МЕТОД"""
        result = self.collection.delete_many(self._filter)
        return result.deleted_count
    
    def update(self, **kwargs):
        """Масове оновлення документів - НОВИЙ МЕТОД"""
        update_data = {}
        for key, value in kwargs.items():
            if key != 'id' and key != '_id':
                update_data[key] = value
        
        result = self.collection.update_many(
            self._filter,
            {'$set': update_data}
        )
        return result.modified_count
    
    def distinct(self, field):
        """Отримати унікальні значення поля - НОВИЙ МЕТОД"""
        return self.collection.distinct(field, self._filter)
    
    def aggregate(self, pipeline):
        """Виконати aggregation pipeline - СТАРИЙ МЕТОД"""
        return list(self.collection.aggregate(pipeline))




class Model(metaclass=ModelMeta):
    """Базова модель для MongoDB"""
    _collection_name = None
    _fields = {}
    _indexes = []  # ← НОВЕ: індекси
    
    def __init__(self, **kwargs):
        # Конвертуємо _id в id - СТАРИЙ КОД
        if '_id' in kwargs:
            self.id = kwargs['_id']
        else:
            self.id = kwargs.get('id', None)
        
        # Ініціалізуємо поля зі значеннями за замовчуванням - ОНОВЛЕНИЙ КОД
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name)
            
            # Якщо значення не передано, використовуємо default
            if value is None:
                # НОВЕ: Якщо default - це функція, викликаємо її
                if callable(field.default):
                    value = field.default()
                else:
                    value = field.default
            
            setattr(self, field_name, value)
        
        # Встановлюємо додаткові атрибути - СТАРИЙ КОД
        for key, value in kwargs.items():
            if key not in self._fields and key not in ['_id', 'id']:
                setattr(self, key, value)
    
    @classmethod
    def get_collection(cls):
        """Отримати колекцію MongoDB - СТАРИЙ МЕТОД"""
        db = get_db()
        return db[cls._collection_name]
    
    @classmethod
    def objects(cls):
        """Отримати QuerySet для запитів - СТАРИЙ МЕТОД"""
        return QuerySet(cls, cls.get_collection())
    
    @classmethod
    def ensure_indexes(cls):
        """Створити індекси для моделі - НОВИЙ МЕТОД"""
        collection = cls.get_collection()
        
        # Створюємо індекси для unique полів
        for field_name, field in cls._fields.items():
            if field.unique:
                try:
                    collection.create_index(field_name, unique=True)
                except Exception as e:
                    print(f"Warning: Could not create index for {field_name}: {e}")
        
        # Створюємо додаткові індекси
        for index in cls._indexes:
            try:
                if isinstance(index, str):
                    collection.create_index(index)
                elif isinstance(index, tuple):
                    collection.create_index([index])
            except Exception as e:
                print(f"Warning: Could not create index {index}: {e}")
    
    def pre_save(self):
        """Hook перед збереженням - НОВИЙ МЕТОД (override в дочірніх класах)"""
        pass
    
    def post_save(self):
        """Hook після збереження - НОВИЙ МЕТОД (override в дочірніх класах)"""
        pass
    
    def save(self):
        """Зберегти документ - ОНОВЛЕНИЙ МЕТОД"""
        # НОВЕ: Hook перед збереженням
        self.pre_save()
        
        data = {}
        
        # Валідація та підготовка даних - СТАРИЙ КОД
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            
            # Debug: print field info if validation fails
            try:
                field.validate(value)
            except ValueError as e:
                import sys
                print(f"VALIDATION ERROR for field '{field_name}': value={value}, type={type(value)}, required={field.required}, default={field.default}", file=sys.stderr)
                raise ValueError(f"Field '{field_name}': {str(e)}")
            
            # Перетворення для MongoDB
            if value is not None:
                data[field_name] = field.to_mongo(value)
        
        collection = self.get_collection()
        
        if self.id:
            # Оновлення існуючого документа - СТАРИЙ КОД
            collection.update_one(
                {'_id': self.id},
                {'$set': data}
            )
        else:
            # Створення нового документа - СТАРИЙ КОД
            result = collection.insert_one(data)
            self.id = result.inserted_id
        
        # НОВЕ: Hook після збереження
        self.post_save()
        
        return self
    
    def delete(self):
        """Видалити документ - СТАРИЙ МЕТОД"""
        if self.id:
            collection = self.get_collection()
            collection.delete_one({'_id': self.id})
            return True
        return False
    
    def to_dict(self, serialize=True):
        """Конвертувати в словник - СТАРИЙ МЕТОД"""
        data = {}
        
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            
            if value is None:
                continue
            
            if serialize:
                # Серіалізація для JSON
                if isinstance(value, ObjectId):
                    data[field_name] = str(value)
                elif isinstance(value, datetime):
                    data[field_name] = value.isoformat()
                elif isinstance(value, list):
                    data[field_name] = [
                        self._serialize_item(item) for item in value
                    ]
                elif isinstance(value, dict):
                    data[field_name] = {
                        k: self._serialize_item(v) for k, v in value.items()
                    }
                else:
                    data[field_name] = value
            else:
                data[field_name] = value
        
        if self.id:
            data['id'] = str(self.id) if serialize else self.id
        
        return data
    
    def _serialize_item(self, item):
        """Серіалізація одного елемента - СТАРИЙ МЕТОД"""
        if isinstance(item, ObjectId):
            return str(item)
        elif isinstance(item, datetime):
            return item.isoformat()
        elif isinstance(item, dict):
            return {k: self._serialize_item(v) for k, v in item.items()}
        elif isinstance(item, (list, tuple)):
            return [self._serialize_item(i) for i in item]
        elif hasattr(item, 'to_dict'):
            return item.to_dict(serialize=True)
        else:
            return item
    
    def get_field_display(self, field_name):
        """Отримати відображення для choices поля - НОВИЙ МЕТОД"""
        field = self._fields.get(field_name)
        if field and hasattr(field, 'choices') and field.choices:
            value = getattr(self, field_name, None)
            return field.get_choices_display(value)
        return getattr(self, field_name, None)
    
    @classmethod
    def find_by_id(cls, id_value):
        """Знайти документ за ID - СТАРИЙ МЕТОД"""
        if isinstance(id_value, str):
            id_value = ObjectId(id_value)
        
        collection = cls.get_collection()
        doc = collection.find_one({'_id': id_value})
        
        return cls(**doc) if doc else None
    
    @classmethod
    def create(cls, **kwargs):
        """Створити та зберегти документ - СТАРИЙ МЕТОД"""
        instance = cls(**kwargs)
        instance.save()
        return instance
    
    def __repr__(self):
        """СТАРИЙ МЕТОД"""
        return f"<{self.__class__.__name__} {self.id}>"
    
    def __str__(self):
        """СТАРИЙ МЕТОД"""
        return self.__repr__()
