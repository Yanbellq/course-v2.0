from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()


class MongoConnection:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoConnection, cls).__new__(cls)
        return cls._instance

    def connect(self):
        if self._client is None:
            try:
                mongodb_uri = os.getenv('MONGODB_URI')
                db_name = os.getenv('MONGODB_DB_NAME', 'pc_management')

                self._client = MongoClient(
                    mongodb_uri,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=10000
                )

                # Перевіряємо з'єднання
                self._client.admin.command('ping')

                # Отримуємо або створюємо базу даних
                self._db = self._client[db_name]

                print(f"✓ MongoDB Atlas з'єднання встановлено: {db_name}")

            except ConnectionFailure as e:
                print(f"✗ Помилка з'єднання з MongoDB: {e}")
                raise
            except Exception as e:
                print(f"✗ Неочікувана помилка: {e}")
                raise

        return self._db

    def get_database(self):
        if self._db is None:
            return self.connect()
        return self._db

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None


# Singleton інстанс
mongo_connection = MongoConnection()


def get_db():
    """Отримати підключення до бази даних"""
    return mongo_connection.get_database()
