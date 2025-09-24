-- SQL скрипт для исправления доступа пользователя 777785057
-- Выполните эти запросы в SQLite браузере или через командную строку

-- 1. Проверяем, есть ли пользователь в базе
SELECT 'Проверка пользователя:' as step;
SELECT * FROM users WHERE user_id = 777785057;

-- 2. Проверяем доступ пользователя
SELECT 'Проверка доступа:' as step;
SELECT * FROM user_access WHERE user_id = 777785057;

-- 3. Проверяем платежи пользователя
SELECT 'Проверка платежей:' as step;
SELECT * FROM payments WHERE user_id = 777785057 ORDER BY created_at DESC;

-- 4. Если пользователя нет, создаем его
INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, created_at)
VALUES (777785057, 'user_777785057', 'User', 'Name', datetime('now'));

-- 5. Создаем активный доступ для пользователя
INSERT OR REPLACE INTO user_access (user_id, payment_type, start_date, end_date, is_active, created_at, updated_at)
VALUES (777785057, 'askeza', datetime('now'), datetime('now', '+30 days'), 1, datetime('now'), datetime('now'));

-- 6. Проверяем результат
SELECT 'Результат после исправления:' as step;
SELECT * FROM user_access WHERE user_id = 777785057;

-- 7. Если нужно создать тестовый платеж
INSERT OR IGNORE INTO payments (user_id, payment_id, payment_type, amount, status, created_at, paid_at)
VALUES (777785057, 'test_payment_777785057', 'askeza', 990, 'succeeded', datetime('now'), datetime('now'));
