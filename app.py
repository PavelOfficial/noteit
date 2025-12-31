"""
NoteIt - Многопользовательское приложение для заметок в формате Markdown
Главный файл приложения Flask
"""
from flask import Flask
from flask_login import LoginManager
from config import Config
from extensions import db
import os


def create_app(config_class=Config):
    """Фабрика приложения Flask"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    
    # Инициализация Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Пожалуйста, войдите в систему для доступа к этой странице.'
    login_manager.login_message_category = 'info'
    
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Регистрация Blueprints
    from blueprints.auth import auth_bp
    from blueprints.documents import documents_bp
    from blueprints.folders import folders_bp
    from blueprints.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(folders_bp, url_prefix='/folders')
    
    # Создание таблиц базы данных
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

