import os
from pathlib import Path
from decouple import config
from dotenv import load_dotenv
# JWT налаштування
from datetime import timedelta
import logging

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
ROOT_URLCONF = 'electronic.urls'
WSGI_APPLICATION = 'electronic.wsgi.application'

DATABASES = {}


SECRET_KEY = config('SECRET_KEY', default='django-insecure-default-key')
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = [config('RENDER_EXTERNAL_HOSTNAME', default=''), 'localhost', '127.0.0.1', 'course-v2-0.onrender.com']
# CORS
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:8000',
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

CSRF_ARRAY = [f"https://{h}" for h in ALLOWED_HOSTS if h]
CSRF_TRUSTED_ORIGINS = ['http://localhost:3000', 'http://localhost:8000'] + CSRF_ARRAY
CSRF_COOKIE_SECURE = False

SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'
SESSION_COOKIE_AGE = 86400  # 24 години
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = False

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS (для production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True



INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.crm',
    'apps.main',
    'apps.api',
]

# MIDDLEWARE = [
#     'django.middleware.security.SecurityMiddleware',
#     'whitenoise.middleware.WhiteNoiseMiddleware',
#     'corsheaders.middleware.CorsMiddleware',
#     'django.contrib.sessions.middleware.SessionMiddleware',
#     'django.middleware.common.CommonMiddleware',
#     'django.middleware.csrf.CsrfViewMiddleware',
#     'django.contrib.messages.middleware.MessageMiddleware',
#     'django.middleware.clickjacking.XFrameOptionsMiddleware',
#     'apps.api.middleware.AuthenticationMiddleware',
# ]

# ✅ MIDDLEWARE В ПРАВИЛЬНОМУ ПОРЯДКУ
MIDDLEWARE = [
    # 1. CORS - ПЕРШИЙ!
    'corsheaders.middleware.CorsMiddleware',
    
    # 2. Security (Django вбудований)
    'django.middleware.security.SecurityMiddleware',
    
    # 3. WhiteNoise (якщо використовуєте)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # 4. Sessions (для Django templates)
    'django.contrib.sessions.middleware.SessionMiddleware',

    # 🟩 ДОДАЙ ОЦЕ (перед Django messages)
    'apps.api.middleware.jwt_web.JWTWebAuthenticationMiddleware',
    
    # 5. Common
    'django.middleware.common.CommonMiddleware',
    
    # 6. CSRF (для Django forms)
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # 7. Messages (для Django templates)
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # 8. Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # ===== ВЛАСНІ MIDDLEWARE =====
    
    # 9. Security перевірки (SQL injection, XSS)
    'apps.api.middleware.security.SecurityMiddleware',
    
    # 10. Rate limiting (захист від DDoS)
    'apps.api.middleware.rate_limit.RateLimitMiddleware',
    
    # 11. JWT автентифікація (для API)
    'apps.api.middleware.jwt_auth.JWTAuthenticationMiddleware',
    
    # 12. Role-based access (перевірка ролей)
    'apps.api.middleware.role_based.RoleBasedAccessMiddleware',
    
    # 13. Request logging (завжди останній!)
    'apps.api.middleware.request_logging.RequestLoggingMiddleware',
    
    # 14. IP Whitelist (опціонально, для admin)
    # 'apps.api.middleware.ip_whitelist.IPWhitelistMiddleware',
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.api.authentication.user_jwt_authentication.MongoJWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
}

# JWT налаштування (свої)
JWT_SECRET_KEY = SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_ACCESS_TOKEN_LIFETIME = 86400  # 24 години в секундах
JWT_REFRESH_TOKEN_LIFETIME = 604800  # 7 днів в секундах

# Login URL for Django @login_required decorator
LOGIN_URL = '/auth/'

# Cache (для rate limiting)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'api_requests.log'),
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'errors.log'),
            'maxBytes': 1024 * 1024 * 10,
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'api': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django': {
            'handlers': ['console', 'error_file'],
            'level': 'INFO',
        },
    },
}

# IP Whitelist (опціонально)
IP_WHITELIST = [
    '127.0.0.1',
    # Додайте ваші trusted IP
]

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]



# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles', 'dist')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static', 'dist')]


# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

WHITENOISE_USE_FINDERS = True
WHITENOISE_AUTOREFRESH = DEBUG
WHITENOISE_SKIP_COMPRESS_EXTENSIONS = ['map', 'json']

# ============ EMAIL CONFIGURATION ============
# Email backend налаштування
# Для development використовуйте console backend (виводить в консоль)
# Для production використовуйте SMTP backend

if DEBUG:
    # Development: виводить email в консоль
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    # Production: використовує SMTP
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# SMTP налаштування (для production)
# Додайте ці змінні в ваш .env файл:
# EMAIL_HOST=smtp.gmail.com (або інший SMTP сервер)
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-app-password
# DEFAULT_FROM_EMAIL=your-email@gmail.com

EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

# Альтернативні варіанти для різних провайдерів:
# 
# Gmail:
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# Потрібно створити "App Password" в налаштуваннях Google Account
#
# Outlook/Hotmail:
# EMAIL_HOST = 'smtp-mail.outlook.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
#
# SendGrid (рекомендовано для production):
# EMAIL_HOST = 'smtp.sendgrid.net'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'apikey'
# EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
#
# Mailgun:
# EMAIL_HOST = 'smtp.mailgun.org'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True