from pathlib import Path
from decouple import config
from mongoengine import connect, disconnect
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [config('RENDER_EXTERNAL_HOSTNAME', default=''), 'localhost', '127.0.0.1', 'course-v2-0.onrender.com']

CSRF_ARRAY = [f"https://{h}" for h in ALLOWED_HOSTS if h]

CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000'] + CSRF_ARRAY
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.customers',
    'apps.suppliers',
    'apps.contracts',
    'apps.products',
    'apps.sales',
    'apps.warranties',
    'apps.repairs',
    'apps.services',
    'apps.custom_pc',
    'apps.employees',
    'rest_framework',
    'apps.main',
    'apps.crm',
    'apps.api',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pc_management.urls'

CORS_ALLOW_ALL_ORIGINS = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'pc_management.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# MongoDB налаштування
MONGODB_SETTINGS = {
    'db': 'PCManagement',
    'host': config('MONGODB_HOST'),
    'username': config('MONGODB_USER'),
    'password': config('MONGODB_PASSWORD'),
    'authentication_source': 'admin',
}

# Підключення до MongoDB
try:
    disconnect()
    connect(**MONGODB_SETTINGS)
except Exception as e:
    print(f"MongoDB connection error: {e}")

# Відключаємо міграції для Django ORM
MIGRATION_MODULES = {
    'auth': None,
    'contenttypes': None,
    'default': None,
    'sessions': None,
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

LANGUAGE_CODE = 'uk-ua'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

# Статичні файли
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
