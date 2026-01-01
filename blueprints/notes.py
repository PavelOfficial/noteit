"""
Blueprint для API работы с заметками
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Document

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/search', methods=['GET'])
@login_required
def search_by_title():
    """
    API эндпоинт для поиска заметок по заголовку
    
    Query параметры:
        query (str): Поисковый запрос для поиска в заголовках заметок
    
    Returns:
        JSON объект с результатами поиска:
        {
            "success": true,
            "count": количество найденных заметок,
            "notes": [
                {
                    "id": int,
                    "title": str,
                    "created_at": str,
                    "updated_at": str,
                    "is_favorite": bool,
                    "is_archived": bool,
                    "folder_id": int или null
                },
                ...
            ]
        }
    
    Пример запроса:
        GET /notes/search?query=заголовок
    """
    # Получаем параметр query из запроса
    query_param = request.args.get('query', '').strip()
    
    # Валидация: проверяем, что параметр query передан
    if not query_param:
        return jsonify({
            'success': False,
            'error': 'Параметр query обязателен для поиска',
            'message': 'Укажите параметр query в запросе'
        }), 400
    
    # Поиск заметок по заголовку (только для текущего пользователя)
    # Используем ilike для регистронезависимого поиска
    documents = Document.query.filter(
        Document.user_id == current_user.id,
        Document.title.ilike(f'%{query_param}%')
    ).order_by(Document.updated_at.desc()).all()
    
    # Формируем JSON ответ
    notes_list = []
    for doc in documents:
        notes_list.append({
            'id': doc.id,
            'title': doc.title,
            'created_at': doc.created_at.isoformat() if doc.created_at else None,
            'updated_at': doc.updated_at.isoformat() if doc.updated_at else None,
            'is_favorite': doc.is_favorite,
            'is_archived': doc.is_archived,
            'folder_id': doc.folder_id
        })
    
    return jsonify({
        'success': True,
        'count': len(notes_list),
        'query': query_param,
        'notes': notes_list
    }), 200

