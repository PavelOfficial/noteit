"""
Конфигурация приложения NoteIt
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Базовая конфигурация"""
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY не установлен. Установите переменную окружения SECRET_KEY.\n"
            "Для генерации случайного ключа используйте: python -c \"import secrets; print(secrets.token_hex(32))\""
        )
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///noteit.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # Установить в True для отладки SQL-запросов
    
    # Настройки безопасности
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Настройки сессии
    PERMANENT_SESSION_LIFETIME = 86400  # 24 часа в секундах
    SESSION_COOKIE_SECURE = False  # True для HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

