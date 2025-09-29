import sqlite3
from datetime import datetime
from contextlib import contextmanager

class Database:
    def __init__(self, db_path="payments.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with self.connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    payment_id TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
    
    @contextmanager
    def connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def add_payment(self, user_id, payment_id, amount):
        """Добавление платежа в БД"""
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO payments (user_id, payment_id, amount, status) VALUES (?, ?, ?, ?)",
                (user_id, payment_id, amount, 'pending')
            )
    
    def update_payment_status(self, payment_id, status):
        """Обновление статуса платежа"""
        with self.connection() as conn:
            completed_at = datetime.now() if status == 'succeeded' else None
            conn.execute(
                "UPDATE payments SET status = ?, completed_at = ? WHERE payment_id = ?",
                (status, completed_at, payment_id)
            )
    
    def get_user_payment(self, user_id):
        """Получение информации о платеже пользователя"""
        with self.connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            return cursor.fetchone()
    
    def add_user(self, user_id, username, first_name, last_name):
        """Добавление пользователя в БД"""
        with self.connection() as conn:
            conn.execute(
                '''INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) 
                VALUES (?, ?, ?, ?)''',
                (user_id, username, first_name, last_name)
            )