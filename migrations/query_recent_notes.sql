-- SQL-запрос для получения 5 самых недавно обновленных заметок для конкретного пользователя
-- с соединением с таблицей users для получения username

-- Вариант 1: Использование INNER JOIN (рекомендуемый)
SELECT 
    n.id,
    n.title,
    n.content,
    n.created_at,
    n.updated_at,
    n.user_id,
    u.username
FROM notes n
INNER JOIN users u ON n.user_id = u.id
WHERE n.user_id = ?
ORDER BY n.updated_at DESC
LIMIT 5;

-- Вариант 2: Использование простого JOIN (эквивалентно INNER JOIN в SQLite)
SELECT 
    n.id,
    n.title,
    n.content,
    n.created_at,
    n.updated_at,
    n.user_id,
    u.username
FROM notes n
JOIN users u ON n.user_id = u.id
WHERE n.user_id = ?
ORDER BY n.updated_at DESC
LIMIT 5;

-- Вариант 3: С использованием алиасов таблиц (более читаемый)
SELECT 
    notes.id,
    notes.title,
    notes.content,
    notes.created_at,
    notes.updated_at,
    notes.user_id,
    users.username
FROM notes
JOIN users ON notes.user_id = users.id
WHERE notes.user_id = ?
ORDER BY notes.updated_at DESC
LIMIT 5;

-- Пример использования с конкретным user_id (например, user_id = 1):
-- SELECT 
--     n.id,
--     n.title,
--     n.content,
--     n.created_at,
--     n.updated_at,
--     n.user_id,
--     u.username
-- FROM notes n
-- INNER JOIN users u ON n.user_id = u.id
-- WHERE n.user_id = 1
-- ORDER BY n.updated_at DESC
-- LIMIT 5;

