#!/usr/bin/env python3
"""
База данных для бота с подписками
"""

import sqlite3
from datetime import datetime, timedelta
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from config import config

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Инициализация базы данных"""
        with self.connection() as conn:
            # Таблица пользователей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Таблица подписок
            conn.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    payment_id TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT FALSE,
                    subscription_type TEXT DEFAULT 'askeza',
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Добавляем поле subscription_type если его нет
            try:
                conn.execute('ALTER TABLE subscriptions ADD COLUMN subscription_type TEXT DEFAULT "askeza"')
            except:
                pass  # Поле уже существует
            
            # Таблица платежей
            conn.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    payment_id TEXT UNIQUE NOT NULL,
                    amount REAL NOT NULL,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Таблица уведомлений
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    notification_type TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
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
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Добавление пользователя в БД"""
        with self.connection() as conn:
            conn.execute(
                '''INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) 
                VALUES (?, ?, ?, ?)''',
                (user_id, username, first_name, last_name)
            )
    
    def update_user_activity(self, user_id: int):
        """Обновление времени последней активности"""
        with self.connection() as conn:
            conn.execute(
                "UPDATE users SET last_activity = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,)
            )
    
    def add_payment(self, user_id: int, payment_id: str, amount: float):
        """Добавление платежа в БД"""
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO payments (user_id, payment_id, amount, status) VALUES (?, ?, ?, ?)",
                (user_id, payment_id, amount, 'pending')
            )
    
    def update_payment_status(self, payment_id: str, status: str):
        """Обновление статуса платежа"""
        with self.connection() as conn:
            completed_at = datetime.now() if status == 'succeeded' else None
            conn.execute(
                "UPDATE payments SET status = ?, completed_at = ? WHERE payment_id = ?",
                (status, completed_at, payment_id)
            )
    
    def get_user_payment(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение последнего платежа пользователя"""
        with self.connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM payments WHERE user_id = ? ORDER BY created_at DESC LIMIT 1",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def create_subscription(self, user_id: int, payment_id: str, amount: float, subscription_type: str = "askeza"):
        """Создание подписки"""
        with self.connection() as conn:
            expires_at = datetime.now() + timedelta(days=config.SUBSCRIPTION_DAYS)
            conn.execute(
                '''INSERT INTO subscriptions (user_id, payment_id, amount, status, expires_at, is_active, subscription_type) 
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (user_id, payment_id, amount, 'active', expires_at, True, subscription_type)
            )
    
    def get_user_subscription(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получение активной подписки пользователя"""
        with self.connection() as conn:
            cursor = conn.execute(
                '''SELECT * FROM subscriptions 
                WHERE user_id = ? AND is_active = TRUE 
                ORDER BY created_at DESC LIMIT 1''',
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def is_subscription_active(self, user_id: int) -> bool:
        """Проверка активности подписки"""
        subscription = self.get_user_subscription(user_id)
        if not subscription:
            return False
        
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        return datetime.now() < expires_at
    
    def get_expiring_subscriptions(self, days: int = None) -> List[Dict[str, Any]]:
        """Получение подписок, истекающих через указанное количество дней"""
        if days is None:
            days = config.WARNING_DAYS
        
        with self.connection() as conn:
            cursor = conn.execute(
                '''SELECT s.*, u.username, u.first_name 
                FROM subscriptions s 
                JOIN users u ON s.user_id = u.user_id 
                WHERE s.is_active = TRUE 
                AND DATE(s.expires_at) = DATE('now', '+{} days')'''.format(days)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def get_expired_subscriptions(self) -> List[Dict[str, Any]]:
        """Получение истекших подписок"""
        with self.connection() as conn:
            cursor = conn.execute(
                '''SELECT s.*, u.username, u.first_name 
                FROM subscriptions s 
                JOIN users u ON s.user_id = u.user_id 
                WHERE s.is_active = TRUE 
                AND s.expires_at < CURRENT_TIMESTAMP'''
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def deactivate_subscription(self, user_id: int):
        """Деактивация подписки"""
        with self.connection() as conn:
            conn.execute(
                "UPDATE subscriptions SET is_active = FALSE WHERE user_id = ? AND is_active = TRUE",
                (user_id,)
            )
    
    def add_notification(self, user_id: int, notification_type: str):
        """Добавление записи об отправленном уведомлении"""
        with self.connection() as conn:
            conn.execute(
                "INSERT INTO notifications (user_id, notification_type) VALUES (?, ?)",
                (user_id, notification_type)
            )
    
    def was_notification_sent(self, user_id: int, notification_type: str, days: int = 1) -> bool:
        """Проверка, было ли отправлено уведомление за последние дни"""
        with self.connection() as conn:
            cursor = conn.execute(
                '''SELECT COUNT(*) as count FROM notifications 
                WHERE user_id = ? AND notification_type = ? 
                AND sent_at > datetime('now', '-{} days')'''.format(days),
                (user_id, notification_type)
            )
            return cursor.fetchone()['count'] > 0
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Получение всех пользователей"""
        with self.connection() as conn:
            cursor = conn.execute("SELECT * FROM users ORDER BY joined_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def get_user_stats(self) -> Dict[str, int]:
        """Получение статистики пользователей"""
        with self.connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            cursor = conn.execute(
                "SELECT COUNT(*) as active FROM subscriptions WHERE is_active = TRUE"
            )
            active_subscriptions = cursor.fetchone()['active']
            
            return {
                'total_users': total_users,
                'active_subscriptions': active_subscriptions
            }
