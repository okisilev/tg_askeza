#!/usr/bin/env python3
"""
Скрипт для исправления доступа пользователя 777785057
"""

import sqlite3
import asyncio
from datetime import datetime

def check_user_in_database(user_id: int):
    """Проверка пользователя в базе данных"""
    print(f"🔍 Проверка пользователя {user_id} в базе данных")
    print("=" * 50)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем пользователя
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        
        if user:
            print("✅ Пользователь найден в базе данных:")
            print(f"   ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   First Name: {user[2]}")
            print(f"   Last Name: {user[3]}")
            print(f"   Created: {user[4]}")
        else:
            print("❌ Пользователь НЕ найден в базе данных")
            return False
        
        # Проверяем доступ пользователя
        cursor.execute("""
            SELECT * FROM user_access 
            WHERE user_id = ? AND is_active = 1
            ORDER BY created_at DESC
        """, (user_id,))
        access = cursor.fetchone()
        
        if access:
            print("\n✅ У пользователя есть активный доступ:")
            print(f"   Тип доступа: {access[2]}")
            print(f"   Дата начала: {access[3]}")
            print(f"   Дата окончания: {access[4]}")
            print(f"   Активен: {access[5]}")
        else:
            print("\n❌ У пользователя НЕТ активного доступа")
            return False
        
        # Проверяем платежи пользователя
        cursor.execute("""
            SELECT * FROM payments 
            WHERE user_id = ? 
            ORDER BY created_at DESC
        """, (user_id,))
        payments = cursor.fetchall()
        
        if payments:
            print(f"\n💳 Найдено {len(payments)} платежей:")
            for payment in payments:
                print(f"   - ID: {payment[0]}")
                print(f"     Тип: {payment[2]}")
                print(f"     Сумма: {payment[3]}₽")
                print(f"     Статус: {payment[4]}")
                print(f"     Дата: {payment[5]}")
                if payment[6]:  # paid_at
                    print(f"     Оплачен: {payment[6]}")
        else:
            print("\n❌ Платежи не найдены")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def create_access_for_user(user_id: int, payment_type: str = "askeza"):
    """Создание доступа для пользователя"""
    print(f"\n🔧 Создание доступа для пользователя {user_id}")
    print("=" * 50)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже доступ
        cursor.execute("""
            SELECT * FROM user_access 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        existing_access = cursor.fetchone()
        
        if existing_access:
            print("⚠️ У пользователя уже есть активный доступ")
            print("Обновляем дату окончания...")
            
            # Обновляем дату окончания
            new_end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                UPDATE user_access 
                SET end_date = ?, updated_at = ?
                WHERE user_id = ? AND is_active = 1
            """, (new_end_date, new_end_date, user_id))
        else:
            print("Создаем новый доступ...")
            
            # Создаем новый доступ
            start_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            end_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO user_access (user_id, payment_type, start_date, end_date, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (user_id, payment_type, start_date, end_date, start_date, start_date))
        
        conn.commit()
        conn.close()
        
        print("✅ Доступ создан/обновлен успешно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании доступа: {e}")
        return False

def print_manual_instructions():
    """Печать инструкций для ручного исправления"""
    print("\n" + "=" * 50)
    print("📋 ИНСТРУКЦИИ ДЛЯ РУЧНОГО ИСПРАВЛЕНИЯ")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте базу данных:")
    print("   • Откройте файл askeza_bot.db в SQLite браузере")
    print("   • Проверьте таблицу 'users' - есть ли пользователь 777785057")
    print("   • Проверьте таблицу 'user_access' - есть ли активный доступ")
    print("   • Проверьте таблицу 'payments' - есть ли успешные платежи")
    
    print("\n2️⃣ Если пользователь есть, но нет доступа:")
    print("   • Создайте запись в таблице 'user_access'")
    print("   • Установите is_active = 1")
    print("   • Установите подходящую дату окончания")
    
    print("\n3️⃣ Если пользователя нет в базе:")
    print("   • Создайте запись в таблице 'users'")
    print("   • Добавьте user_id = 777785057")
    print("   • Создайте доступ в таблице 'user_access'")
    
    print("\n4️⃣ Проверьте настройки бота:")
    print("   • PRIVATE_CHANNEL_ID должен быть настроен")
    print("   • Бот должен быть администратором канала")
    print("   • У бота должны быть права на приглашение пользователей")
    
    print("\n5️⃣ Отправьте пользователю пригласительную ссылку:")
    print("   • Используйте функцию send_channel_invite")
    print("   • Или отправьте ссылку вручную")
    print("   • Попросите пользователя подписаться и нажать 'Проверить подписку'")

def main():
    """Основная функция"""
    user_id = 777785057
    
    print("🚨 ИСПРАВЛЕНИЕ ДОСТУПА ПОЛЬЗОВАТЕЛЯ")
    print("=" * 50)
    
    # Проверяем пользователя в базе данных
    user_exists = check_user_in_database(user_id)
    
    if user_exists:
        print("\n🔧 Пытаемся исправить доступ...")
        success = create_access_for_user(user_id)
        
        if success:
            print("\n✅ Доступ исправлен!")
            print("Теперь пользователь должен:")
            print("1. Нажать 'Закрытый канал' в боте")
            print("2. Получить пригласительную ссылку")
            print("3. Подписаться на канал по ссылке")
            print("4. Нажать 'Проверить подписку'")
        else:
            print("\n❌ Не удалось автоматически исправить доступ")
            print_manual_instructions()
    else:
        print("\n❌ Пользователь не найден в базе данных")
        print_manual_instructions()

if __name__ == "__main__":
    main()
