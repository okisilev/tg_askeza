#!/usr/bin/env python3
"""
Быстрое исправление доступа для пользователя 777785057
"""

import sqlite3
from datetime import datetime, timedelta

def quick_fix_user():
    """Быстрое исправление доступа пользователя"""
    user_id = 777785057
    
    print(f"🔧 Быстрое исправление доступа для пользователя {user_id}")
    print("=" * 50)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # 1. Создаем пользователя, если его нет
        print("1. Создаем пользователя...")
        cursor.execute("""
            INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, f'user_{user_id}', 'User', 'Name', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
        # 2. Создаем активный доступ
        print("2. Создаем активный доступ...")
        start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT OR REPLACE INTO user_access (user_id, payment_type, start_date, end_date, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, 'askeza', start_date, end_date, 1, start_date, start_date))
        
        # 3. Создаем тестовый платеж
        print("3. Создаем тестовый платеж...")
        cursor.execute("""
            INSERT OR IGNORE INTO payments (user_id, payment_id, payment_type, amount, status, created_at, paid_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, f'test_payment_{user_id}', 'askeza', 990, 'succeeded', start_date, start_date))
        
        # Сохраняем изменения
        conn.commit()
        
        # Проверяем результат
        print("4. Проверяем результат...")
        cursor.execute("SELECT * FROM user_access WHERE user_id = ?", (user_id,))
        access = cursor.fetchone()
        
        if access:
            print("✅ Доступ создан успешно!")
            print(f"   Пользователь: {user_id}")
            print(f"   Тип доступа: {access[2]}")
            print(f"   Дата начала: {access[3]}")
            print(f"   Дата окончания: {access[4]}")
            print(f"   Активен: {access[5]}")
        else:
            print("❌ Не удалось создать доступ")
        
        conn.close()
        
        print("\n📋 Следующие шаги:")
        print("1. Перезапустите бота")
        print("2. Попросите пользователя нажать 'Закрытый канал'")
        print("3. Пользователь получит пригласительную ссылку")
        print("4. Пользователь подписывается по ссылке")
        print("5. Пользователь нажимает 'Проверить подписку'")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = quick_fix_user()
    
    if success:
        print("\n✅ Проблема решена!")
    else:
        print("\n❌ Не удалось решить проблему автоматически")
        print("Попробуйте выполнить SQL скрипт fix_user_777785057.sql вручную")
