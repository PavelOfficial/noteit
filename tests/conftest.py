"""
Конфигурация и фикстуры для тестирования
"""
import pytest
from app import create_app
from extensions import db
from models import User


class TestConfig:
    """Тестовая конфигурация"""
    SECRET_KEY = 'test-secret-key-for-testing-only'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False  # Отключаем CSRF для тестов
    TESTING = True


@pytest.fixture
def app():
    """Создание тестового приложения"""
    # Создаем тестовое приложение с тестовой конфигурацией
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Тестовый клиент Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Тестовый CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Сессия базы данных для тестов"""
    with app.app_context():
        yield db.session


@pytest.fixture
def sample_user(db_session):
    """Создание тестового пользователя"""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('testpass123')
    db_session.add(user)
    db_session.commit()
    return user

