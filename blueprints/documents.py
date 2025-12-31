"""
Blueprint для работы с документами
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Document, Folder
from blueprints.forms import DocumentForm, SearchForm
from markdown import markdown
from bleach import clean

documents_bp = Blueprint('documents', __name__)


def get_user_folders():
    """Получить список папок пользователя для формы"""
    folders = Folder.query.filter_by(user_id=current_user.id).order_by(Folder.name).all()
    return [(0, 'Без папки')] + [(f.id, f.name) for f in folders]


@documents_bp.route('/')
@login_required
def list_documents():
    """Список всех документов пользователя"""
    page = request.args.get('page', 1, type=int)
    folder_id = request.args.get('folder_id', None, type=int)
    is_favorite = request.args.get('favorite', False, type=bool)
    is_archived = request.args.get('archived', False, type=bool)
    
    query = Document.query.filter_by(user_id=current_user.id)
    
    if folder_id:
        query = query.filter_by(folder_id=folder_id)
    
    if is_favorite:
        query = query.filter_by(is_favorite=True)
    
    if is_archived:
        query = query.filter_by(is_archived=True)
    else:
        query = query.filter_by(is_archived=False)
    
    documents = query.order_by(Document.updated_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    folders = Folder.query.filter_by(user_id=current_user.id).order_by(Folder.name).all()
    
    return render_template('documents/list.html',
                         documents=documents,
                         folders=folders,
                         current_folder_id=folder_id,
                         is_favorite=is_favorite,
                         is_archived=is_archived)


@documents_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_document():
    """Создание нового документа"""
    form = DocumentForm()
    form.folder_id.choices = get_user_folders()
    
    # Получение folder_id из параметров запроса (если создается из папки)
    folder_id_param = request.args.get('folder_id', None, type=int)
    if folder_id_param:
        form.folder_id.data = folder_id_param
    
    if form.validate_on_submit():
        # Проверка папки
        folder_id = form.folder_id.data if form.folder_id.data else None
        if folder_id:
            folder = Folder.query.filter_by(id=folder_id, user_id=current_user.id).first()
            if not folder:
                flash('Папка не найдена.', 'danger')
                return redirect(url_for('documents.create_document'))
        
        # Конвертация Markdown в HTML
        content_html = markdown(form.content.data)
        # Очистка HTML от потенциально опасных тегов
        content_html = clean(content_html, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                                  'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'],
                            attributes={'a': ['href'], 'img': ['src', 'alt']})
        
        document = Document(
            title=form.title.data,
            content=form.content.data,
            content_html=content_html,
            user_id=current_user.id,
            folder_id=folder_id,
            is_favorite=form.is_favorite.data,
            is_archived=form.is_archived.data
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash('Документ успешно создан!', 'success')
        return redirect(url_for('documents.view_document', id=document.id))
    
    return render_template('documents/form.html', form=form, title='Создать документ')


@documents_bp.route('/<int:id>')
@login_required
def view_document(id):
    """Просмотр документа"""
    document = Document.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Если HTML не сгенерирован, сгенерировать его
    if not document.content_html:
        document.content_html = markdown(document.content)
        document.content_html = clean(document.content_html, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                                          'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'],
                                  attributes={'a': ['href'], 'img': ['src', 'alt']})
        db.session.commit()
    
    return render_template('documents/view.html', document=document)


@documents_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(id):
    """Редактирование документа"""
    document = Document.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = DocumentForm(obj=document)
    form.folder_id.choices = get_user_folders()
    
    if form.validate_on_submit():
        # Проверка папки
        folder_id = form.folder_id.data if form.folder_id.data else None
        if folder_id:
            folder = Folder.query.filter_by(id=folder_id, user_id=current_user.id).first()
            if not folder:
                flash('Папка не найдена.', 'danger')
                return redirect(url_for('documents.edit_document', id=id))
        
        # Обновление документа
        document.title = form.title.data
        document.content = form.content.data
        document.folder_id = folder_id
        document.is_favorite = form.is_favorite.data
        document.is_archived = form.is_archived.data
        
        # Обновление HTML
        document.content_html = markdown(document.content)
        document.content_html = clean(document.content_html, tags=['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                                                          'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img'],
                                  attributes={'a': ['href'], 'img': ['src', 'alt']})
        
        db.session.commit()
        
        flash('Документ успешно обновлен!', 'success')
        return redirect(url_for('documents.view_document', id=document.id))
    
    return render_template('documents/form.html', form=form, document=document, title='Редактировать документ')


@documents_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_document(id):
    """Удаление документа"""
    document = Document.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    db.session.delete(document)
    db.session.commit()
    
    flash('Документ успешно удален!', 'success')
    return redirect(url_for('documents.list_documents'))


@documents_bp.route('/<int:id>/toggle-favorite', methods=['POST'])
@login_required
def toggle_favorite(id):
    """Переключение статуса избранного"""
    document = Document.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    document.is_favorite = not document.is_favorite
    db.session.commit()
    
    return jsonify({'success': True, 'is_favorite': document.is_favorite})


@documents_bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    """Поиск документов"""
    form = SearchForm()
    documents = []
    
    if form.validate_on_submit() or request.args.get('query'):
        query_text = form.query.data or request.args.get('query', '')
        
        if query_text:
            # Поиск по заголовку и содержимому
            documents = Document.query.filter(
                Document.user_id == current_user.id,
                Document.is_archived == False,
                db.or_(
                    Document.title.ilike(f'%{query_text}%'),
                    Document.content.ilike(f'%{query_text}%')
                )
            ).order_by(Document.updated_at.desc()).all()
            
            if not documents:
                flash('Ничего не найдено.', 'info')
    
    return render_template('documents/search.html', form=form, documents=documents)

