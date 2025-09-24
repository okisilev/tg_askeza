import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from config import DATABASE_PATH

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблица пользователей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            # Таблица платежей
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    payment_type TEXT, -- 'askeza' или 'numerology'
                    amount REAL,
                    yookassa_payment_id TEXT UNIQUE,
                    status TEXT DEFAULT 'pending', -- 'pending', 'succeeded', 'canceled'
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    paid_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица доступа
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS access (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    access_type TEXT, -- 'askeza' или 'numerology'
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("База данных инициализирована")
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Добавление нового пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя {user_id}: {e}")
            return None
    
    def create_payment(self, user_id: int, payment_type: str, amount: float, yookassa_payment_id: str) -> bool:
        """Создание записи о платеже"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (user_id, payment_type, amount, yookassa_payment_id)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, payment_type, amount, yookassa_payment_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return False
    
    def update_payment_status(self, yookassa_payment_id: str, status: str) -> bool:
        """Обновление статуса платежа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payments 
                    SET status = ?, paid_at = CURRENT_TIMESTAMP
                    WHERE yookassa_payment_id = ?
                ''', (status, yookassa_payment_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса платежа: {e}")
            return False
    
    def get_payment(self, yookassa_payment_id: str) -> Optional[Dict[str, Any]]:
        """Получение информации о платеже"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM payments WHERE yookassa_payment_id = ?', (yookassa_payment_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Ошибка при получении платежа: {e}")
            return None
    
    def grant_access(self, user_id: int, access_type: str) -> bool:
        """Предоставление доступа пользователю"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                expires_at = datetime.now() + timedelta(days=30)
                cursor.execute('''
                    INSERT INTO access (user_id, access_type, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, access_type, expires_at))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Ошибка при предоставлении доступа: {e}")
            return False
    
    def get_user_access(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение активного доступа пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM access 
                    WHERE user_id = ? AND is_active = TRUE AND expires_at > CURRENT_TIMESTAMP
                ''', (user_id,))
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении доступа пользователя: {e}")
            return []
    
    def revoke_expired_access(self) -> int:
        """Отзыв истекшего доступа"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE access 
                    SET is_active = FALSE 
                    WHERE expires_at <= CURRENT_TIMESTAMP AND is_active = TRUE
                ''')
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"Ошибка при отзыве истекшего доступа: {e}")
            return 0
    
    def get_expired_users(self) -> List[int]:
        """Получение пользователей с истекшим доступом"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DISTINCT user_id FROM access 
                    WHERE expires_at <= CURRENT_TIMESTAMP AND is_active = TRUE
                ''')
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении пользователей с истекшим доступом: {e}")
            return []
