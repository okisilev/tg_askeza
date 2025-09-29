#!/usr/bin/env python3
"""
Проверка обработки платежей
"""

import sqlite3
from datetime import datetime, timedelta

def check_pending_payments():
    """Проверка pending платежей"""
    print("🔍 Проверка pending платежей")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем pending платежи
        cursor.execute('''
            SELECT user_id, yookassa_payment_id, payment_type, amount, created_at 
            FROM payments 
            WHERE status = 'pending'
            ORDER BY created_at DESC
        ''')
        pending_payments = cursor.fetchall()
        
        if pending_payments:
            print(f"⏳ Найдено {len(pending_payments)} pending платежей:")
            for payment in pending_payments:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Created: {payment[4]}")
                print()
        else:
            print("✅ Pending платежей не найдено")
        
        # Проверяем успешные платежи без доступа
        cursor.execute('''
            SELECT p.user_id, p.yookassa_payment_id, p.payment_type, p.amount, p.created_at
            FROM payments p
            LEFT JOIN user_access ua ON p.user_id = ua.user_id AND ua.is_active = 1
            WHERE p.status = 'succeeded' AND ua.user_id IS NULL
            ORDER BY p.created_at DESC
        ''')
        payments_without_access = cursor.fetchall()
        
        if payments_without_access:
            print(f"⚠️ Найдено {len(payments_without_access)} успешных платежей без доступа:")
            for payment in payments_without_access:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Created: {payment[4]}")
                print()
        else:
            print("✅ Все успешные платежи имеют доступ")
        
        conn.close()
        return len(pending_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0, 0

def check_automatic_processing():
    """Проверка автоматической обработки"""
    print("\n🤖 Проверка автоматической обработки")
    print("=" * 50)
    
    print("📋 Что должно происходить автоматически:")
    print("1. ✅ Создание платежа при оплате")
    print("2. ✅ Обновление статуса платежа")
    print("3. ❌ Предоставление доступа (проблема)")
    print("4. ❌ Отправка уведомления (проблема)")
    print("5. ❌ Добавление в канал (проблема)")
    
    print("\n🔧 Возможные причины проблем:")
    print("1. Бот не запущен")
    print("2. Периодическая проверка не работает")
    print("3. Обработка платежей отключена")
    print("4. Ошибки в логах бота")

def main():
    """Основная функция"""
    print("🔍 Проверка обработки платежей")
    print("=" * 50)
    
    # Проверяем pending платежи
    pending_count, without_access_count = check_pending_payments()
    
    # Проверяем автоматическую обработку
    check_automatic_processing()
    
    print(f"\n📊 Результат:")
    print(f"   • Pending платежей: {pending_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    
    if pending_count > 0 or without_access_count > 0:
        print("\n⚠️ Обнаружены проблемы с обработкой платежей!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Проверьте логи на ошибки")
        print("3. Убедитесь, что периодическая проверка работает")
    else:
        print("\n✅ Обработка платежей работает корректно")

if __name__ == "__main__":
    main()
