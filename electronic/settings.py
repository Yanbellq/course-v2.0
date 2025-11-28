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

MIDDLEWARE = [
    # 1. CORS - ПЕРШИЙ!
    'corsheaders.middleware.CorsMiddleware',
    
    # 2. Security (Django вбудований)
    'django.middleware.security.SecurityMiddleware',
    
    # 3. WhiteNoise (якщо використовуєте)
    'whitenoise.middleware.WhiteNoiseMiddleware',
    
    # 4. Sessions (для Django templates)
    'django.contrib.sessions.middleware.SessionMiddleware',

    # 5. JWT автентифікація (для API)
    'apps.api.middleware.jwt_web.JWTWebAuthenticationMiddleware',
    
    # 6. Common
    'django.middleware.common.CommonMiddleware',
    
    # 7. CSRF (для Django forms)
    'django.middleware.csrf.CsrfViewMiddleware',
    
    # 8. Messages (для Django templates)
    'django.contrib.messages.middleware.MessageMiddleware',
    
    # 9. Clickjacking protection
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 10. Security перевірки (SQL injection, XSS)
    'apps.api.middleware.security.SecurityMiddleware',
    
    # 11. Rate limiting (захист від DDoS)
    'apps.api.middleware.rate_limit.RateLimitMiddleware',
    
    # 12. JWT автентифікація (для API)
    'apps.api.middleware.jwt_auth.JWTAuthenticationMiddleware',
    
    # 13. Role-based access (перевірка ролей)
    'apps.api.middleware.role_based.RoleBasedAccessMiddleware',
    
    # 14. Request logging (завжди останній!)
    'apps.api.middleware.request_logging.RequestLoggingMiddleware',
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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Gmail SMTP налаштування
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER or 'noreply@electronic.com')

# Таймаут для SMTP з'єднання (в секундах)
EMAIL_TIMEOUT = config('EMAIL_TIMEOUT', default=10, cast=int)

# Логування налаштувань email (без пароля)
import logging
logger = logging.getLogger('api')
logger.info(f"Email configuration: HOST={EMAIL_HOST}, PORT={EMAIL_PORT}, USE_TLS={EMAIL_USE_TLS}, USER={EMAIL_HOST_USER}, FROM={DEFAULT_FROM_EMAIL}")
logger.info(f"Email backend: {EMAIL_BACKEND}")
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    logger.warning("WARNING: EMAIL налаштування не заповнені! Email не будуть відправлятися.")
    logger.warning("Для Gmail потрібно створити App Password:")
    logger.warning("1. Увійдіть в Google Account: https://myaccount.google.com/")
    logger.warning("2. Перейдіть: Security → 2-Step Verification")
    logger.warning("3. В кінці сторінки знайдіть 'App passwords'")
    logger.warning("4. Створіть новий App Password для 'Mail'")
    logger.warning("5. Використовуйте цей App Password в EMAIL_HOST_PASSWORD")