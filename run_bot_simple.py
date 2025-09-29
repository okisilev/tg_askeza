#!/usr/bin/env python3
"""
Простой запуск бота для автоматической обработки платежей
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from yookassa_client import YooKassaClient
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_payments():
    """Проверка платежей"""
    print("🔍 Проверка платежей")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Проверяем pending платежи
        cursor = db.conn.cursor()
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
        
        return len(pending_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка при проверке платежей: {e}")
        return 0, 0

def main():
    """Основная функция"""
    print("🚀 Проверка автоматической обработки платежей")
    print("=" * 50)
    
    # Проверяем текущее состояние
    pending_count, without_access_count = check_payments()
    
    print(f"\n📊 Текущее состояние:")
    print(f"   • Pending платежей: {pending_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    
    if without_access_count > 0:
        print("\n⚠️ Обнаружены платежи без доступа!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Или исправьте вручную: python fix_all_payments.py")
    else:
        print("\n✅ Все платежи обработаны корректно")
    
    print("\n💡 Для автоматической обработки запустите:")
    print("   python run_no_webhook.py")
    print("\n📋 Что происходит автоматически:")
    print("1. ✅ Создание платежа при оплате")
    print("2. ✅ Обновление статуса платежа")
    print("3. ✅ Предоставление доступа")
    print("4. ✅ Отправка уведомления с кнопками")
    print("5. ✅ Добавление в канал")

if __name__ == "__main__":
    main()
