"""
Blueprint для работы с папками
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Folder, Document
from blueprints.forms import FolderForm

folders_bp = Blueprint('folders', __name__)


def get_user_folders(exclude_id=None):
    """Получить список папок пользователя для формы (исключая указанную)"""
    folders = Folder.query.filter_by(user_id=current_user.id, parent_id=None).order_by(Folder.name).all()
    choices = [(0, 'Корневая папка')]
    
    def add_folder_recursive(folder, level=0):
        if exclude_id and folder.id == exclude_id:
            return
        choices.append((folder.id, '  ' * level + folder.name))
        for child in folder.children.order_by(Folder.name).all():
            add_folder_recursive(child, level + 1)
    
    for folder in folders:
        add_folder_recursive(folder)
    
    return choices


@folders_bp.route('/')
@login_required
def list_folders():
    """Список всех папок пользователя"""
    folders = Folder.query.filter_by(user_id=current_user.id, parent_id=None).order_by(Folder.name).all()
    return render_template('folders/list.html', folders=folders)


@folders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_folder():
    """Создание новой папки"""
    form = FolderForm()
    form.parent_id.choices = get_user_folders()
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data else None
        
        # Проверка родительской папки
        if parent_id:
            parent = Folder.query.filter_by(id=parent_id, user_id=current_user.id).first()
            if not parent:
                flash('Родительская папка не найдена.', 'danger')
                return redirect(url_for('folders.create_folder'))
        
        folder = Folder(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id,
            parent_id=parent_id
        )
        
        db.session.add(folder)
        db.session.commit()
        
        flash('Папка успешно создана!', 'success')
        return redirect(url_for('folders.view_folder', id=folder.id))
    
    return render_template('folders/form.html', form=form, title='Создать папку')


@folders_bp.route('/<int:id>')
@login_required
def view_folder(id):
    """Просмотр папки"""
    folder = Folder.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Получаем документы в папке
    documents = Document.query.filter_by(folder_id=id, user_id=current_user.id, is_archived=False).order_by(Document.updated_at.desc()).all()
    
    # Получаем дочерние папки
    children = Folder.query.filter_by(parent_id=id, user_id=current_user.id).order_by(Folder.name).all()
    
    return render_template('folders/view.html', folder=folder, documents=documents, children=children)


@folders_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_folder(id):
    """Редактирование папки"""
    folder = Folder.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = FolderForm(obj=folder)
    form.parent_id.choices = get_user_folders(exclude_id=id)
    
    if form.validate_on_submit():
        parent_id = form.parent_id.data if form.parent_id.data else None
        
        # Проверка родительской папки (нельзя сделать папку родителем самой себя)
        if parent_id == id:
            flash('Папка не может быть родителем самой себя.', 'danger')
            return redirect(url_for('folders.edit_folder', id=id))
        
        if parent_id:
            parent = Folder.query.filter_by(id=parent_id, user_id=current_user.id).first()
            if not parent:
                flash('Родительская папка не найдена.', 'danger')
                return redirect(url_for('folders.edit_folder', id=id))
        
        folder.name = form.name.data
        folder.description = form.description.data
        folder.parent_id = parent_id
        
        db.session.commit()
        
        flash('Папка успешно обновлена!', 'success')
        return redirect(url_for('folders.view_folder', id=folder.id))
    
    return render_template('folders/form.html', form=form, folder=folder, title='Редактировать папку')


@folders_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_folder(id):
    """Удаление папки"""
    folder = Folder.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    
    # Проверка наличия документов и дочерних папок
    documents_count = Document.query.filter_by(folder_id=id, user_id=current_user.id).count()
    children_count = Folder.query.filter_by(parent_id=id, user_id=current_user.id).count()
    
    if documents_count > 0 or children_count > 0:
        flash('Невозможно удалить папку: в ней есть документы или подпапки.', 'danger')
        return redirect(url_for('folders.view_folder', id=id))
    
    db.session.delete(folder)
    db.session.commit()
    
    flash('Папка успешно удалена!', 'success')
    return redirect(url_for('folders.list_folders'))

