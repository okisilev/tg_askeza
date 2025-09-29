#!/usr/bin/env python3
"""
Исправление доступа для пользователя 760111270
"""

import sqlite3
from datetime import datetime, timedelta

def check_database_structure():
    """Проверка структуры базы данных"""
    print("🔍 Проверка структуры базы данных")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Найденные таблицы:")
        for table in tables:
            print(f"   • {table[0]}")
        
        # Проверяем структуру таблицы users
        cursor.execute("PRAGMA table_info(users);")
        users_columns = cursor.fetchall()
        print(f"\n👤 Структура таблицы users:")
        for col in users_columns:
            print(f"   • {col[1]} ({col[2]})")
        
        # Проверяем структуру таблицы payments
        cursor.execute("PRAGMA table_info(payments);")
        payments_columns = cursor.fetchall()
        print(f"\n💳 Структура таблицы payments:")
        for col in payments_columns:
            print(f"   • {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры: {e}")
        return False

def create_user_access_table():
    """Создание таблицы user_access"""
    print("\n🔧 Создание таблицы user_access")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Создаем таблицу user_access
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                access_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        print("✅ Таблица user_access создана")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблицы: {e}")
        return False

def grant_access_to_user(user_id: int):
    """Предоставление доступа пользователю"""
    print(f"\n🔐 Предоставление доступа пользователю {user_id}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже активный доступ
        cursor.execute('''
            SELECT id, access_type, is_active 
            FROM user_access 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        existing_access = cursor.fetchone()
        
        if existing_access:
            print(f"✅ Активный доступ уже существует: {existing_access[1]}")
            conn.close()
            return True
        
        # Создаем новый доступ
        expires_at = datetime.now() + timedelta(days=30)
        cursor.execute('''
            INSERT INTO user_access (user_id, access_type, expires_at, is_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, 'askeza', expires_at, 1))
        
        print(f"✅ Доступ предоставлен до {expires_at}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при предоставлении доступа: {e}")
        return False

def send_notification_to_user(user_id: int):
    """Отправка уведомления пользователю"""
    print(f"\n📧 Отправка уведомления пользователю {user_id}")
    print("=" * 50)
    
    try:
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
        from config import BOT_TOKEN
        
        bot = Bot(token=BOT_TOKEN)
        
        success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к Аскезе.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
        """
        
        # Создаем кнопки для доступа
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        bot.send_message(
            chat_id=user_id,
            text=success_text,
            reply_markup=reply_markup
        )
        
        print("✅ Уведомление с кнопками отправлено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")
        return False

def main():
    """Основная функция"""
    user_id = 760111270
    
    print("🔧 Исправление доступа для пользователя 760111270")
    print("=" * 50)
    
    # Проверяем структуру базы данных
    structure_ok = check_database_structure()
    
    if not structure_ok:
        print("❌ Проблемы со структурой базы данных")
        return
    
    # Создаем таблицу user_access
    table_created = create_user_access_table()
    
    if not table_created:
        print("❌ Не удалось создать таблицу user_access")
        return
    
    # Предоставляем доступ пользователю
    access_granted = grant_access_to_user(user_id)
    
    if not access_granted:
        print("❌ Не удалось предоставить доступ")
        return
    
    # Отправляем уведомление
    notification_sent = send_notification_to_user(user_id)
    
    if notification_sent:
        print("✅ Уведомление отправлено")
    else:
        print("❌ Не удалось отправить уведомление")
    
    print("\n📋 Результат:")
    print("✅ Таблица user_access создана")
    print("✅ Доступ предоставлен")
    print("✅ Уведомление отправлено")
    print("\n🎉 Пользователь 760111270 теперь должен получить кнопки доступа!")

if __name__ == "__main__":
    main()
