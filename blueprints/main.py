"""
Главный Blueprint для основных страниц
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import Document, Folder

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Панель управления пользователя"""
    # Получаем последние документы
    recent_documents = Document.query.filter_by(
        user_id=current_user.id,
        is_archived=False
    ).order_by(Document.updated_at.desc()).limit(10).all()
    
    # Получаем избранные документы
    favorite_documents = Document.query.filter_by(
        user_id=current_user.id,
        is_favorite=True,
        is_archived=False
    ).order_by(Document.updated_at.desc()).limit(5).all()
    
    # Получаем папки
    folders = Folder.query.filter_by(
        user_id=current_user.id,
        parent_id=None
    ).order_by(Folder.name).all()
    
    # Статистика
    total_documents = Document.query.filter_by(user_id=current_user.id, is_archived=False).count()
    total_folders = Folder.query.filter_by(user_id=current_user.id).count()
    
    return render_template('dashboard.html',
                         recent_documents=recent_documents,
                         favorite_documents=favorite_documents,
                         folders=folders,
                         total_documents=total_documents,
                         total_folders=total_folders)

