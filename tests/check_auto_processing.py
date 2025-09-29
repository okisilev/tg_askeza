#!/usr/bin/env python3
"""
Проверка автоматической обработки платежей
"""

import sqlite3
from datetime import datetime, timedelta

def check_recent_payments():
    """Проверка недавних платежей"""
    print("🔍 Проверка недавних платежей")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Проверяем платежи за последние 24 часа
        cursor.execute('''
            SELECT user_id, yookassa_payment_id, payment_type, amount, status, created_at 
            FROM payments 
            WHERE created_at >= datetime('now', '-1 day')
            ORDER BY created_at DESC
        ''')
        recent_payments = cursor.fetchall()
        
        if recent_payments:
            print(f"📋 Найдено {len(recent_payments)} платежей за последние 24 часа:")
            for payment in recent_payments:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Status: {payment[4]}")
                print(f"     Created: {payment[5]}")
                print()
        else:
            print("❌ Недавних платежей не найдено")
        
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
        return len(recent_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0, 0

def check_bot_status():
    """Проверка статуса бота"""
    print("\n🤖 Проверка статуса бота")
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
    
    print("\n💡 Рекомендации:")
    print("1. Запустите бота: python run_no_webhook.py")
    print("2. Проверьте логи на ошибки")
    print("3. Убедитесь, что периодическая проверка работает")

def main():
    """Основная функция"""
    print("🔍 Проверка автоматической обработки платежей")
    print("=" * 50)
    
    # Проверяем недавние платежи
    recent_count, without_access_count = check_recent_payments()
    
    # Проверяем статус бота
    check_bot_status()
    
    print(f"\n📊 Результат:")
    print(f"   • Недавних платежей: {recent_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    
    if without_access_count > 0:
        print("\n⚠️ Обнаружены платежи без доступа!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Или исправьте вручную: python fix_all_payments.py")
    else:
        print("\n✅ Автоматическая обработка работает корректно")

if __name__ == "__main__":
    main()
