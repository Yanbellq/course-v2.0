from core.mongo_connection import get_db

# Ініціалізація підключення при запуску
try:
    db = get_db()
    print("✓ MongoDB підключено успішно")
except Exception as e:
    print(f"✗ Помилка підключення до MongoDB: {e}")
