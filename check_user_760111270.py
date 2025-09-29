#!/usr/bin/env python3
"""
Проверка пользователя 760111270 в базе данных
"""

import sqlite3
from datetime import datetime

def check_user_in_database():
    """Проверка пользователя в базе данных"""
    print("🔍 Проверка пользователя 760111270 в базе данных")
    print("=" * 50)
    
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем пользователя
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (760111270,))
        user = cursor.fetchone()
        
        if user:
            print(f"✅ Пользователь найден:")
            print(f"   • ID: {user[0]}")
            print(f"   • Username: {user[1]}")
            print(f"   • First name: {user[2]}")
            print(f"   • Last name: {user[3]}")
            print(f"   • Created: {user[4]}")
        else:
            print("❌ Пользователь не найден в базе данных")
            return False
        
        # Проверяем платежи
        cursor.execute('''
            SELECT yookassa_payment_id, payment_type, amount, status, created_at 
            FROM payments 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (760111270,))
        payments = cursor.fetchall()
        
        if payments:
            print(f"\n📋 Найдено {len(payments)} платежей:")
            for payment in payments:
                print(f"   • ID: {payment[0]}")
                print(f"     Тип: {payment[1]}")
                print(f"     Сумма: {payment[2]}₽")
                print(f"     Статус: {payment[3]}")
                print(f"     Дата: {payment[4]}")
                print()
        else:
            print("❌ Платежей не найдено")
            return False
        
        # Проверяем успешные платежи
        successful_payments = [p for p in payments if p[3] == 'succeeded']
        if successful_payments:
            print(f"✅ Успешных платежей: {len(successful_payments)}")
            for payment in successful_payments:
                print(f"   • {payment[0]} - {payment[1]} - {payment[2]}₽ - {payment[4]}")
        else:
            print("❌ Успешных платежей не найдено")
            return False
        
        # Проверяем доступ
        cursor.execute('''
            SELECT access_type, created_at, expires_at, is_active 
            FROM user_access 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (760111270,))
        access_records = cursor.fetchall()
        
        if access_records:
            print(f"\n🔐 Найдено {len(access_records)} записей доступа:")
            for access in access_records:
                print(f"   • Тип: {access[0]}")
                print(f"     Создан: {access[1]}")
                print(f"     Истекает: {access[2]}")
                print(f"     Активен: {access[3]}")
                print()
        else:
            print("❌ Записей доступа не найдено")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def print_troubleshooting():
    """Печать инструкций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 УСТРАНЕНИЕ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Если пользователь не найден:")
    print("   • Пользователь должен сначала написать боту /start")
    print("   • Проверьте, что бот работает")
    print("   • Убедитесь, что пользователь не заблокировал бота")
    
    print("\n2️⃣ Если платеж не найден:")
    print("   • Проверьте, что платеж был создан через бота")
    print("   • Убедитесь, что платеж не был отменен")
    print("   • Проверьте, что статус платежа обновился")
    
    print("\n3️⃣ Если доступ не предоставлен:")
    print("   • Запустите бота для автоматической обработки")
    print("   • Проверьте логи на ошибки")
    print("   • Убедитесь, что платеж успешный")
    
    print("\n4️⃣ Если кнопки не появляются:")
    print("   • Проверьте, что бот может отправлять сообщения")
    print("   • Убедитесь, что обработка платежей работает")
    print("   • Проверьте, что уведомления отправляются")

def main():
    """Основная функция"""
    print("🔍 Проверка пользователя 760111270")
    print("=" * 50)
    
    # Проверяем базу данных
    db_ok = check_user_in_database()
    
    if db_ok:
        print("✅ База данных проверена")
    else:
        print("❌ Проблемы с базой данных")
        print_troubleshooting()
        return
    
    print("\n📋 Рекомендации:")
    print("1. Если пользователь не найден - он должен написать боту /start")
    print("2. Если платеж не найден - проверьте создание платежа")
    print("3. Если доступ не предоставлен - запустите бота")
    print("4. Если кнопки не появляются - проверьте обработку платежей")

if __name__ == "__main__":
    main()
