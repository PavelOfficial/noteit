-- SQL оператор для создания таблицы notes в SQLite
-- Таблица для хранения заметок пользователей

-- Включаем поддержку внешних ключей (требуется для SQLite)
PRAGMA foreign_keys = ON;

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

-- Создаем индекс для user_id для улучшения производительности запросов
CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);

-- Создаем индекс для created_at для быстрой сортировки по дате
CREATE INDEX IF NOT EXISTS idx_notes_created_at ON notes(created_at);

-- Создаем индекс для title для быстрого поиска по заголовку
CREATE INDEX IF NOT EXISTS idx_notes_title ON notes(title);

