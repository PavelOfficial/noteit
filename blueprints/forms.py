"""
Формы для NoteIt
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class LoginForm(FlaskForm):
    """Форма входа"""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    """Форма регистрации"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(), 
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Введите корректный email адрес')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=6, message='Пароль должен содержать минимум 6 символов')
    ])
    password2 = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Зарегистрироваться')


class DocumentForm(FlaskForm):
    """Форма создания/редактирования документа"""
    title = StringField('Заголовок', validators=[
        DataRequired(), 
        Length(min=1, max=200, message='Заголовок должен быть от 1 до 200 символов')
    ])
    content = TextAreaField('Содержание (Markdown)', validators=[DataRequired()])
    folder_id = SelectField('Папка', coerce=int, validators=[Optional()], choices=[])
    is_favorite = BooleanField('Избранное')
    is_archived = BooleanField('Архив')
    submit = SubmitField('Сохранить')


class FolderForm(FlaskForm):
    """Форма создания/редактирования папки"""
    name = StringField('Название папки', validators=[
        DataRequired(), 
        Length(min=1, max=100, message='Название должно быть от 1 до 100 символов')
    ])
    description = TextAreaField('Описание', validators=[Optional(), Length(max=500)])
    parent_id = SelectField('Родительская папка', coerce=int, validators=[Optional()], choices=[])
    submit = SubmitField('Сохранить')


class SearchForm(FlaskForm):
    """Форма поиска"""
    query = StringField('Поиск', validators=[DataRequired(), Length(min=1, max=200)])
    submit = SubmitField('Найти')

