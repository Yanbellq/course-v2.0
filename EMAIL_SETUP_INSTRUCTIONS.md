# Інструкція з налаштування відправки email для відновлення пароля

## 📧 Налаштування email в Django

### 1. Додайте змінні в `.env` файл

Створіть або оновіть файл `.env` в корені проекту з наступними змінними:

```env
# Email налаштування
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_HOST_PASSWORD="uooc liyy umtr rmem"
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 2. Варіанти налаштування для різних провайдерів

#### Gmail (Google)

1. Увійдіть в ваш Google Account
2. Перейдіть в **Безпека** → **Двофакторна автентифікація** (увімкніть, якщо не увімкнена)
3. Перейдіть в **Паролі додатків**
4. Створіть новий пароль додатку для "Пошта" та "Інший (назва користувача)"
5. Скопіюйте згенерований пароль (16 символів)
6. Використовуйте цей пароль як `EMAIL_HOST_PASSWORD`

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop  # Пароль додатку
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### Outlook/Hotmail

```env
EMAIL_HOST=smtp-mail.outlook.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=your-email@outlook.com
```

#### SendGrid (Рекомендовано для production)

1. Зареєструйтеся на [SendGrid](https://sendgrid.com/)
2. Створіть API Key
3. Використовуйте наступні налаштування:

```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

#### Mailgun

```env
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@your-domain.mailgun.org
EMAIL_HOST_PASSWORD=your-mailgun-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 3. Development режим (локальна розробка)

В development режимі (`DEBUG=True`) email будуть виводитися в консоль замість реальної відправки. Це налаштовано автоматично в `settings.py`:

```python
if DEBUG:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### 4. Тестування відправки email

#### Тест через Django shell:

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Subject',
    'Test message',
    settings.DEFAULT_FROM_EMAIL,
    ['recipient@example.com'],
    fail_silently=False,
)
```

#### Тест через API:

1. Запустіть сервер: `python manage.py runserver`
2. Відкрийте Postman або використайте curl:

```bash
curl -X POST http://localhost:8000/api/user/auth/forgot-password/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### 5. Перевірка налаштувань

Перевірте, чи правильно налаштовані змінні:

```python
from django.conf import settings

print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
```

### 6. Troubleshooting

#### Помилка: "SMTPAuthenticationError"

- Перевірте правильність email та пароля
- Для Gmail: використовуйте пароль додатку, не звичайний пароль
- Переконайтеся, що двофакторна автентифікація увімкнена (для Gmail)

#### Помилка: "Connection refused"

- Перевірте, чи правильний порт (587 для TLS, 465 для SSL)
- Перевірте налаштування файрволу
- Переконайтеся, що `EMAIL_USE_TLS` або `EMAIL_USE_SSL` правильно налаштовані

#### Email не відправляються в production

- Перевірте, чи `DEBUG=False` в production
- Перевірте логи сервера на наявність помилок
- Використовуйте спеціалізовані сервіси (SendGrid, Mailgun) для production

### 7. Безпека

⚠️ **Важливо:**
- Ніколи не комітьте `.env` файл в Git
- Використовуйте окремі email акаунти для development та production
- Для production використовуйте спеціалізовані email сервіси (SendGrid, Mailgun)
- Обмежте кількість email на хвилину (rate limiting)

### 8. Додаткові налаштування

#### Rate limiting для email

Додайте в `settings.py`:

```python
# Обмеження кількості email
EMAIL_RATE_LIMIT = {
    'forgot_password': 3,  # максимум 3 email на годину для одного користувача
}
```

#### Асинхронна відправка email (Celery)

Для великих проектів рекомендовано використовувати Celery для асинхронної відправки:

```python
# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_password_reset_email_async(user_email, reset_url):
    # ... код відправки
    pass
```

### 9. Шаблони email

Шаблони знаходяться в:
- `templates/emails/password_reset.html` - HTML версія
- `templates/emails/password_reset.txt` - текстова версія

Ви можете кастомізувати їх під ваш дизайн.

---

## ✅ Чеклист для запуску

- [ ] Додано змінні в `.env` файл
- [ ] Налаштовано SMTP сервер
- [ ] Протестовано відправку email в development
- [ ] Налаштовано production email сервіс (SendGrid/Mailgun)
- [ ] Додано `.env` в `.gitignore`
- [ ] Протестовано відновлення пароля через UI

---

**Примітка:** Для локальної розробки email будуть виводитися в консоль. Для production обов'язково налаштуйте реальний SMTP сервер.

