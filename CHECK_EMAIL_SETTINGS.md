# 🔍 Перевірка налаштувань Email

## Проблема: Email не відправляються

Якщо email не відправляються, виконайте наступні кроки:

### 1. Перевірте змінні середовища на Render

На Render.com перевірте, чи додані всі змінні в **Environment Variables**:

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=uooc liyy umtr rmem
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**⚠️ Важливо:** 
- `EMAIL_HOST_PASSWORD` має бути **без лапок** в змінних середовища Render
- Якщо в `.env` файлі є лапки: `EMAIL_HOST_PASSWORD="uooc liyy umtr rmem"`, то в Render додайте БЕЗ лапок: `uooc liyy umtr rmem`

### 2. Перевірте логи сервера

Після деплою перевірте логи на Render. Ви повинні побачити:

```
INFO Email configuration: HOST=smtp.gmail.com, PORT=587, USER=your-email@gmail.com, FROM=your-email@gmail.com
INFO Email backend: django.core.mail.backends.smtp.EmailBackend
```

Якщо бачите попередження:
```
WARNING ⚠️ EMAIL налаштування не заповнені! Email не будуть відправлятися.
```

Це означає, що змінні не завантажилися правильно.

### 3. Перевірка через Django shell на Render

Якщо можливо, підключіться до сервера і перевірте:

```python
from django.conf import settings
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
```

### 4. Типові проблеми

#### Проблема: Змінні не завантажуються

**Рішення:**
- Перевірте, чи правильно названі змінні (великі літери)
- Переконайтеся, що немає пробілів навколо `=`
- Перезапустіть сервіс на Render після додавання змінних

#### Проблема: SMTP Authentication Error

**Рішення:**
- Для Gmail: переконайтеся, що використовуєте **App Password**, а не звичайний пароль
- Перевірте, чи увімкнена двофакторна автентифікація
- Переконайтеся, що пароль додатку правильний (без пробілів, якщо вони не потрібні)

#### Проблема: Connection refused

**Рішення:**
- Перевірте, чи правильний порт (587 для TLS)
- Перевірте, чи `EMAIL_USE_TLS=True` (не SSL)
- Можливо, Render блокує з'єднання - спробуйте використати SendGrid замість Gmail

### 5. Альтернатива: Використання SendGrid

Якщо Gmail не працює на Render, використайте SendGrid:

1. Зареєструйтеся на [SendGrid](https://sendgrid.com/)
2. Створіть API Key
3. Додайте в Render Environment Variables:

```
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### 6. Тестування відправки

Після налаштування, спробуйте відправити email через forgot password. Перевірте логи:

**Успішна відправка:**
```
INFO Attempting to send password reset email to user@example.com
INFO Sending email from your-email@gmail.com to user@example.com
INFO Email sent successfully to user@example.com
```

**Помилка:**
```
ERROR Failed to send password reset email to user@example.com: [деталі помилки]
ERROR SMTP error when sending email to user@example.com: [деталі помилки]
```

### 7. Швидка перевірка

Додайте в `.env` файл (для локального тестування):

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=uooc liyy umtr rmem
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

Запустіть локально і перевірте, чи працює. Якщо працює локально, але не на Render - проблема в налаштуваннях змінних середовища на Render.

---

**Найчастіша проблема:** Змінні середовища на Render не завантажуються або мають неправильні значення. Перевірте їх уважно!

