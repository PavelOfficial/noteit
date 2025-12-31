"""
Blueprint для аутентификации
"""
import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from extensions import db
from models import User
from blueprints.forms import LoginForm, RegistrationForm

auth_bp = Blueprint('auth', __name__)


def validate_email_format(email):
    """
    Дополнительная проверка формата email
    
    Args:
        email: Email адрес для проверки
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not email:
        return False, 'Email не может быть пустым'
    
    # Нормализация: приведение к нижнему регистру и удаление пробелов
    email = email.strip().lower()
    
    # Базовый паттерн для проверки формата email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, 'Некорректный формат email адреса'
    
    # Проверка на минимальную длину домена верхнего уровня (минимум 2 символа)
    parts = email.split('@')
    if len(parts) != 2:
        return False, 'Некорректный формат email адреса'
    
    domain_parts = parts[1].split('.')
    if len(domain_parts) < 2 or len(domain_parts[-1]) < 2:
        return False, 'Email должен содержать корректный домен верхнего уровня (например, .com, .org)'
    
    # Проверка на максимальную длину email (RFC 5321)
    if len(email) > 254:
        return False, 'Email адрес слишком длинный (максимум 254 символа)'
    
    # Проверка на максимальную длину локальной части (до @)
    local_part = parts[0]
    if len(local_part) > 64:
        return False, 'Локальная часть email слишком длинная (максимум 64 символа)'
    
    return True, None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Обрабатывает регистрацию нового пользователя в системе.
    
    Эндпоинт поддерживает два HTTP метода:
    - GET: Отображает форму регистрации для неавторизованных пользователей.
           Авторизованные пользователи перенаправляются на dashboard.
    - POST: Обрабатывает данные формы регистрации, валидирует их,
            создает нового пользователя в базе данных и перенаправляет
            на страницу входа при успешной регистрации.
    
    Процесс регистрации включает следующие этапы:
    1. Проверка авторизации пользователя (редирект, если авторизован)
    2. Валидация данных формы через WTForms
    3. Нормализация email (приведение к нижнему регистру, удаление пробелов)
    4. Дополнительная валидация формата email
    5. Проверка уникальности username и email в базе данных
    6. Создание нового пользователя с хешированием пароля
    7. Сохранение в базу данных с обработкой возможных конфликтов
    
    Args:
        Нет явных параметров. Функция использует Flask request context:
        - form.email.data: Email адрес пользователя из формы
        - form.username.data: Имя пользователя из формы
        - form.password.data: Пароль пользователя из формы
        - form.password2.data: Подтверждение пароля из формы
        - current_user: Текущий пользователь из Flask-Login (для проверки авторизации)
    
    Returns:
        flask.Response: HTTP ответ в зависимости от сценария:
            - GET запрос: HTML страница с формой регистрации (status 200)
            - POST успешная регистрация: Редирект на /auth/login (status 302)
            - POST ошибка валидации: HTML страница с формой и сообщениями об ошибках (status 200)
            - Авторизованный пользователь: Редирект на /dashboard (status 302)
    
    Raises:
        sqlalchemy.exc.IntegrityError: Может возникнуть при сохранении в БД,
            если нарушены ограничения уникальности (обрабатывается внутри функции).
            В этом случае выполняется rollback транзакции и возвращается форма с ошибкой.
        
        Exception: Могут возникнуть другие исключения при работе с базой данных
            или шаблонами (не обрабатываются явно, должны обрабатываться на уровне приложения).
    
    Note:
        - Email адрес автоматически нормализуется (приводится к нижнему регистру)
          перед сохранением в базу данных для предотвращения дубликатов.
        - Пароль хешируется с использованием Werkzeug (PBKDF2) перед сохранением.
        - Функция использует оптимизированный запрос для проверки существования
          пользователя (один SQL запрос вместо двух).
        - Обрабатывается race condition: если пользователь был создан между
          проверкой и сохранением, IntegrityError перехватывается и обрабатывается.
    
    Example:
        Успешная регистрация::
        
            POST /auth/register
            {
                "username": "newuser",
                "email": "user@example.com",
                "password": "securepass123",
                "password2": "securepass123"
            }
            # Результат: Редирект на /auth/login с сообщением об успехе
        
        Ошибка валидации::
        
            POST /auth/register
            {
                "username": "existing_user",  # уже существует
                "email": "existing@example.com",
                "password": "pass123",
                "password2": "pass123"
            }
            # Результат: Форма регистрации с сообщением об ошибке
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Нормализация и дополнительная проверка email
        email = form.email.data.strip().lower() if form.email.data else ''
        
        # Дополнительная валидация формата email
        is_valid, error_message = validate_email_format(email)
        if not is_valid:
            flash(error_message or 'Некорректный формат email адреса', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Оптимизированная проверка существования пользователя (один запрос вместо двух)
        existing_user = User.query.filter(
            or_(
                User.username == form.username.data,
                User.email == email
            )
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('Пользователь с таким именем уже существует.', 'danger')
            else:
                flash('Пользователь с таким email уже существует.', 'danger')
            return render_template('auth/register.html', form=form)
        
        # Создание нового пользователя с нормализованным email
        user = User(username=form.username.data, email=email)
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash('Ошибка регистрации. Пользователь с такими данными уже существует.', 'danger')
            return render_template('auth/register.html', form=form)
        
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Вход в систему"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        
        flash('Неверное имя пользователя или пароль.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    flash('Вы успешно вышли из системы.', 'info')
    return redirect(url_for('main.index'))

