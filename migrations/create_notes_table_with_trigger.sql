-- SQL оператор для создания таблицы notes с триггером для автоматического обновления updated_at

PRAGMA foreign_keys = ON;

-- Создание таблицы notes
CREATE TABLE IF NOT EXISTS notes (
    -- Первичный ключ: UUID (хранится как TEXT в SQLite)
    id TEXT NOT NULL PRIMARY KEY,
    
    -- Заголовок заметки (обязательное поле)
    title TEXT NOT NULL,
    
    -- Содержимое заметки (может быть NULL)
    content TEXT,
    
    -- Метка времени создания (значение по умолчанию - текущее время)
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    
    -- Метка времени обновления (значение по умолчанию - текущее время)
    updated_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    
    -- Внешний ключ на таблицу users
    user_id INTEGER NOT NULL,
    
    -- Ограничение внешнего ключа
    CONSTRAINT fk_notes_user_id 
        FOREIGN KEY (user_id) 
        REFERENCES users(id) 
        ON DELETE CASCADE 
        ON UPDATE CASCADE
);

-- Триггер для автоматического обновления updated_at при изменении записи
CREATE TRIGGER IF NOT EXISTS update_notes_updated_at
    AFTER UPDATE ON notes
    FOR EACH ROW
    WHEN NEW.updated_at = OLD.updated_at
BEGIN
    UPDATE notes 
    SET updated_at = datetime('now', 'localtime') 
    WHERE id = NEW.id;
END;

-- Индексы для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);

