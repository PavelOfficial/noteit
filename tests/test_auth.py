"""
Модульные тесты для аутентификации
"""
import pytest
from extensions import db
from models import User


class TestRegisterEndpoint:
    """Тесты для эндпоинта /register"""
    
    def test_register_success_with_valid_data(self, client, db_session):
        """
        Тест: Успешная регистрация с валидными данными
        
        Ожидаемое поведение:
        - Пользователь успешно регистрируется
        - Происходит редирект на страницу входа
        - Пользователь создается в базе данных
        - Отображается сообщение об успехе
        """
        # Подготовка данных
        register_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'securepass123',
            'password2': 'securepass123',
            'submit': True
        }
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=False)
        
        # Проверка редиректа
        assert response.status_code == 302
        assert '/auth/login' in response.location
        
        # Проверка создания пользователя в БД
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
        assert user.check_password('securepass123')
        
        # Проверка сообщения об успехе (нужно проверить через follow_redirects)
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        # Проверяем, что пользователь не может зарегистрироваться повторно
        response_text = response.data.decode('utf-8')
        assert 'уже существует' in response_text or response.status_code != 200
    
    def test_register_with_existing_email(self, client, db_session, sample_user):
        """
        Тест: Попытка регистрации с email, который уже есть в базе
        
        Ожидаемое поведение:
        - Регистрация отклоняется
        - Отображается сообщение об ошибке
        - Пользователь не создается
        - Возвращается форма регистрации
        """
        # Подготовка данных с существующим email
        register_data = {
            'username': 'differentuser',
            'email': sample_user.email,  # Используем email существующего пользователя
            'password': 'newpass123',
            'password2': 'newpass123',
            'submit': True
        }
        
        # Подсчет пользователей до попытки регистрации
        users_before = User.query.count()
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка статуса (должна вернуться форма с ошибкой)
        assert response.status_code == 200
        
        # Проверка сообщения об ошибке
        response_text = response.data.decode('utf-8')
        assert 'email уже существует' in response_text or 'Пользователь с таким email уже существует' in response_text
        
        # Проверка, что новый пользователь не создан
        users_after = User.query.count()
        assert users_after == users_before
        
        # Проверка, что пользователь с новым username не создан
        new_user = User.query.filter_by(username='differentuser').first()
        assert new_user is None
    
    def test_register_with_existing_username(self, client, db_session, sample_user):
        """
        Тест: Попытка регистрации с username, который уже есть в базе
        
        Ожидаемое поведение:
        - Регистрация отклоняется
        - Отображается сообщение об ошибке
        - Пользователь не создается
        """
        # Подготовка данных с существующим username
        register_data = {
            'username': sample_user.username,  # Используем username существующего пользователя
            'email': 'different@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'submit': True
        }
        
        # Подсчет пользователей до попытки регистрации
        users_before = User.query.count()
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка статуса
        assert response.status_code == 200
        
        # Проверка сообщения об ошибке
        response_text = response.data.decode('utf-8')
        assert 'имя уже существует' in response_text or 'Пользователь с таким именем уже существует' in response_text
        
        # Проверка, что новый пользователь не создан
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_without_password(self, client, db_session):
        """
        Тест: Попытка регистрации с отсутствующими данными (без пароля)
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        - Пользователь не создается
        - Возвращается форма с ошибками валидации
        """
        # Подготовка данных без пароля
        register_data = {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': '',  # Пустой пароль
            'password2': '',
            'submit': True
        }
        
        # Подсчет пользователей до попытки регистрации
        users_before = User.query.count()
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка статуса (форма должна вернуться с ошибками)
        assert response.status_code == 200
        
        # Проверка, что новый пользователь не создан
        users_after = User.query.count()
        assert users_after == users_before
        
        # Проверка, что форма отображается (не произошел редирект)
        response_text = response.data.decode('utf-8').lower()
        assert 'register' in response_text or 'регистрация' in response_text
    
    def test_register_without_username(self, client, db_session):
        """
        Тест: Попытка регистрации без имени пользователя
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        """
        register_data = {
            'username': '',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'submit': True
        }
        
        users_before = User.query.count()
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        assert response.status_code == 200
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_without_email(self, client, db_session):
        """
        Тест: Попытка регистрации без email
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        """
        register_data = {
            'username': 'testuser3',
            'email': '',
            'password': 'testpass123',
            'password2': 'testpass123',
            'submit': True
        }
        
        users_before = User.query.count()
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        assert response.status_code == 200
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_with_password_mismatch(self, client, db_session):
        """
        Тест: Попытка регистрации с несовпадающими паролями
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        """
        register_data = {
            'username': 'testuser4',
            'email': 'test4@example.com',
            'password': 'password123',
            'password2': 'differentpass',  # Пароли не совпадают
            'submit': True
        }
        
        users_before = User.query.count()
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        assert response.status_code == 200
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_with_short_password(self, client, db_session):
        """
        Тест: Попытка регистрации с коротким паролем (менее 6 символов)
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        """
        register_data = {
            'username': 'testuser5',
            'email': 'test5@example.com',
            'password': 'short',  # Менее 6 символов
            'password2': 'short',
            'submit': True
        }
        
        users_before = User.query.count()
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        assert response.status_code == 200
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_with_invalid_email(self, client, db_session):
        """
        Тест: Попытка регистрации с невалидным email
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        """
        register_data = {
            'username': 'testuser6',
            'email': 'invalid-email',  # Невалидный email
            'password': 'testpass123',
            'password2': 'testpass123',
            'submit': True
        }
        
        users_before = User.query.count()
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        assert response.status_code == 200
        users_after = User.query.count()
        assert users_after == users_before
    
    def test_register_with_malformed_email(self, client, db_session):
        """
        Тест: Попытка регистрации с некорректным форматом email (без домена верхнего уровня)
        
        Пример: test@example (без .com, .org и т.д.)
        
        Ожидаемое поведение:
        - Валидация формы не проходит
        - Регистрация отклоняется
        - Пользователь не создается
        - Возвращается форма с ошибкой валидации email
        """
        register_data = {
            'username': 'testuser7',
            'email': 'test@example',  # Некорректный формат - без домена верхнего уровня
            'password': 'testpass123',
            'password2': 'testpass123',
            'submit': True
        }
        
        # Подсчет пользователей до попытки регистрации
        users_before = User.query.count()
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка статуса (форма должна вернуться с ошибками)
        assert response.status_code == 200
        
        # Проверка сообщения об ошибке валидации email
        response_text = response.data.decode('utf-8')
        assert 'домен верхнего уровня' in response_text or 'Некорректный формат email' in response_text or 'email' in response_text.lower()
        
        # Проверка, что новый пользователь не создан
        users_after = User.query.count()
        assert users_after == users_before
        
        # Проверка, что форма отображается (не произошел редирект)
        response_text_lower = response_text.lower()
        assert 'register' in response_text_lower or 'регистрация' in response_text_lower
        
        # Проверка, что пользователь с таким username не создан
        new_user = User.query.filter_by(username='testuser7').first()
        assert new_user is None
    
    def test_register_with_empty_string_password(self, client, db_session):
        """
        Тест: Попытка регистрации с пустой строкой пароля
        
        Ожидаемое поведение:
        - Валидация формы не проходит (DataRequired валидатор должен сработать)
        - Регистрация отклоняется
        - Пользователь не создается
        - Возвращается форма с ошибками валидации
        """
        register_data = {
            'username': 'testuser8',
            'email': 'test8@example.com',
            'password': '',  # Явно пустая строка
            'password2': '',  # Явно пустая строка
            'submit': True
        }
        
        # Подсчет пользователей до попытки регистрации
        users_before = User.query.count()
        
        # Выполнение запроса
        response = client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка статуса (форма должна вернуться с ошибками)
        assert response.status_code == 200
        
        # Проверка, что новый пользователь не создан
        users_after = User.query.count()
        assert users_after == users_before
        
        # Проверка, что форма отображается (не произошел редирект)
        response_text = response.data.decode('utf-8').lower()
        assert 'register' in response_text or 'регистрация' in response_text
        
        # Проверка, что пользователь с таким username не создан
        new_user = User.query.filter_by(username='testuser8').first()
        assert new_user is None
    
    def test_register_get_request(self, client):
        """
        Тест: GET запрос на страницу регистрации
        
        Ожидаемое поведение:
        - Возвращается форма регистрации
        """
        response = client.get('/auth/register')
        
        assert response.status_code == 200
        response_text = response.data.decode('utf-8').lower()
        assert 'register' in response_text or 'регистрация' in response_text


class TestAuthIntegration:
    """Интеграционные тесты для полных пользовательских сценариев"""
    
    def test_full_user_registration_and_login_flow(self, client, db_session):
        """
        Интеграционный тест: Полный пользовательский сценарий регистрации и входа
        
        Сценарий:
        1. Пользователь регистрируется с валидными данными
        2. Пользователь входит в систему используя зарегистрированные данные
        3. Пользователь получает доступ к защищенным страницам
        
        Ожидаемое поведение:
        - Регистрация проходит успешно
        - Пользователь создается в базе данных
        - Вход в систему проходит успешно
        - Пользователь перенаправляется на dashboard
        - Пользователь может получить доступ к защищенным страницам
        """
        # Шаг 1: Регистрация нового пользователя
        username = 'integration_user'
        email = 'integration@example.com'
        password = 'securepass123'
        
        register_data = {
            'username': username,
            'email': email,
            'password': password,
            'password2': password,
            'submit': True
        }
        
        # Выполнение регистрации
        register_response = client.post('/auth/register', data=register_data, follow_redirects=False)
        
        # Проверка успешной регистрации
        assert register_response.status_code == 302, "Регистрация должна завершиться редиректом"
        assert '/auth/login' in register_response.location, "После регистрации должен быть редирект на страницу входа"
        
        # Проверка создания пользователя в базе данных
        user = User.query.filter_by(username=username).first()
        assert user is not None, "Пользователь должен быть создан в базе данных"
        assert user.email == email.lower(), "Email должен быть нормализован (нижний регистр)"
        assert user.check_password(password), "Пароль должен быть корректно сохранен"
        
        # Шаг 2: Вход в систему
        login_data = {
            'username': username,
            'password': password,
            'remember_me': False,
            'submit': True
        }
        
        # Выполнение входа
        login_response = client.post('/auth/login', data=login_data, follow_redirects=False)
        
        # Проверка успешного входа
        assert login_response.status_code == 302, "Вход должен завершиться редиректом"
        assert '/dashboard' in login_response.location, "После входа должен быть редирект на dashboard"
        
        # Шаг 3: Проверка доступа к защищенной странице (dashboard)
        # После редиректа на dashboard, нужно следовать редиректу
        dashboard_response = client.get('/dashboard', follow_redirects=True)
        
        # Проверка успешного доступа к dashboard
        assert dashboard_response.status_code == 200, "Пользователь должен иметь доступ к dashboard"
        dashboard_text = dashboard_response.data.decode('utf-8').lower()
        assert 'dashboard' in dashboard_text or 'панель' in dashboard_text, "Должна отображаться страница dashboard"
        
        # Шаг 4: Проверка, что пользователь действительно авторизован
        # Попытка доступа к защищенной странице без редиректа
        protected_response = client.get('/dashboard', follow_redirects=False)
        assert protected_response.status_code == 200, "Авторизованный пользователь должен иметь прямой доступ к dashboard"
        
        # Шаг 5: Проверка, что авторизованный пользователь перенаправляется при попытке регистрации
        # (авторизованные пользователи не должны видеть форму регистрации)
        duplicate_register_response = client.post('/auth/register', data=register_data, follow_redirects=False)
        assert duplicate_register_response.status_code == 302, "Авторизованный пользователь должен быть перенаправлен"
        assert '/dashboard' in duplicate_register_response.location, "Должен быть редирект на dashboard для авторизованного пользователя"
        
        # Шаг 6: Выход из системы для проверки повторной регистрации
        client.get('/auth/logout', follow_redirects=True)
        
        # Шаг 7: Попытка повторной регистрации с теми же данными (теперь неавторизованный)
        duplicate_register_response = client.post('/auth/register', data=register_data, follow_redirects=True)
        assert duplicate_register_response.status_code == 200, "Повторная регистрация должна быть отклонена"
        duplicate_text = duplicate_register_response.data.decode('utf-8')
        assert 'уже существует' in duplicate_text, "Должно быть сообщение о существующем пользователе"
        
        # Проверка, что количество пользователей не изменилось
        users_count = User.query.filter_by(username=username).count()
        assert users_count == 1, "Должен быть только один пользователь с таким username"
    
    def test_registration_login_and_logout_flow(self, client, db_session):
        """
        Интеграционный тест: Полный цикл регистрация → вход → выход
        
        Сценарий:
        1. Пользователь регистрируется
        2. Пользователь входит в систему
        3. Пользователь выходит из системы
        4. Пользователь не может получить доступ к защищенным страницам
        
        Ожидаемое поведение:
        - Все шаги выполняются успешно
        - После выхода пользователь не имеет доступа к защищенным страницам
        """
        # Шаг 1: Регистрация
        username = 'logout_test_user'
        email = 'logout@example.com'
        password = 'testpass123'
        
        register_data = {
            'username': username,
            'email': email,
            'password': password,
            'password2': password,
            'submit': True
        }
        
        client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка регистрации
        user = User.query.filter_by(username=username).first()
        assert user is not None, "Пользователь должен быть зарегистрирован"
        
        # Шаг 2: Вход в систему
        login_data = {
            'username': username,
            'password': password,
            'remember_me': False,
            'submit': True
        }
        
        login_response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert login_response.status_code == 200, "Вход должен быть успешным"
        
        # Проверка доступа к защищенной странице
        dashboard_response = client.get('/dashboard', follow_redirects=False)
        assert dashboard_response.status_code == 200, "Авторизованный пользователь должен иметь доступ"
        
        # Шаг 3: Выход из системы
        logout_response = client.get('/auth/logout', follow_redirects=True)
        assert logout_response.status_code == 200, "Выход должен быть успешным"
        
        logout_text = logout_response.data.decode('utf-8')
        assert 'вышли' in logout_text.lower() or 'logout' in logout_text.lower(), "Должно быть сообщение об успешном выходе"
        
        # Шаг 4: Проверка, что после выхода нет доступа к защищенным страницам
        protected_response = client.get('/dashboard', follow_redirects=False)
        assert protected_response.status_code == 302, "Неавторизованный пользователь должен быть перенаправлен"
        assert '/auth/login' in protected_response.location, "Должен быть редирект на страницу входа"
    
    def test_registration_with_normalized_email_and_login(self, client, db_session):
        """
        Интеграционный тест: Регистрация с email в разных регистрах и вход
        
        Сценарий:
        1. Пользователь регистрируется с email в верхнем регистре
        2. Email нормализуется при сохранении
        3. Пользователь входит используя email в любом регистре (через username)
        
        Ожидаемое поведение:
        - Email нормализуется при регистрации
        - Вход работает корректно
        """
        # Шаг 1: Регистрация с email в верхнем регистре
        username = 'case_test_user'
        email_upper = 'CASE_TEST@EXAMPLE.COM'
        email_normalized = 'case_test@example.com'
        password = 'testpass123'
        
        register_data = {
            'username': username,
            'email': email_upper,
            'password': password,
            'password2': password,
            'submit': True
        }
        
        client.post('/auth/register', data=register_data, follow_redirects=True)
        
        # Проверка нормализации email
        user = User.query.filter_by(username=username).first()
        assert user is not None, "Пользователь должен быть создан"
        assert user.email == email_normalized, f"Email должен быть нормализован. Ожидалось: {email_normalized}, получено: {user.email}"
        
        # Шаг 2: Вход в систему
        login_data = {
            'username': username,
            'password': password,
            'remember_me': False,
            'submit': True
        }
        
        login_response = client.post('/auth/login', data=login_data, follow_redirects=True)
        assert login_response.status_code == 200, "Вход должен быть успешным"
        
        # Проверка доступа к защищенной странице
        dashboard_response = client.get('/dashboard', follow_redirects=False)
        assert dashboard_response.status_code == 200, "Пользователь должен иметь доступ после входа"

