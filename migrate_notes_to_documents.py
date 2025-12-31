"""
Скрипт миграции для переименования таблицы notes в documents
ВАЖНО: Создайте резервную копию базы данных перед выполнением миграции!
"""
import sqlite3
import os
from pathlib import Path

# Путь к базе данных
DB_PATH = Path('instance/noteit.db')

def migrate_database():
    """Переименование таблицы notes в documents"""
    if not DB_PATH.exists():
        print(f"База данных не найдена: {DB_PATH}")
        print("Миграция не требуется - база данных будет создана автоматически с новой схемой.")
        return
    
    # Создаем резервную копию
    backup_path = DB_PATH.with_suffix('.db.backup')
    print(f"Создание резервной копии: {backup_path}")
    
    import shutil
    shutil.copy2(DB_PATH, backup_path)
    print("Резервная копия создана успешно!")
    
    # Подключаемся к базе данных
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Проверяем существование таблицы notes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
        if not cursor.fetchone():
            print("Таблица 'notes' не найдена. Миграция не требуется.")
            conn.close()
            return
        
        print("Начинаем миграцию...")
        
        # Переименовываем таблицу
        print("Переименование таблицы 'notes' в 'documents'...")
        cursor.execute("ALTER TABLE notes RENAME TO documents")
        
        # Обновляем индексы (если они есть)
        print("Обновление индексов...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND sql LIKE '%notes%'")
        indexes = cursor.fetchall()
        for index in indexes:
            old_name = index[0]
            new_name = old_name.replace('notes', 'documents')
            print(f"  Переименование индекса: {old_name} -> {new_name}")
            cursor.execute(f"DROP INDEX IF EXISTS {old_name}")
            # Индексы будут пересозданы автоматически при следующем запуске приложения
        
        # Коммитим изменения
        conn.commit()
        print("Миграция завершена успешно!")
        print(f"Резервная копия сохранена в: {backup_path}")
        
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при миграции: {e}")
        print("Откат изменений...")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("Миграция базы данных: notes -> documents")
    print("=" * 60)
    print()
    
    response = input("Вы уверены, что хотите выполнить миграцию? (yes/no): ")
    if response.lower() != 'yes':
        print("Миграция отменена.")
        exit(0)
    
    migrate_database()

