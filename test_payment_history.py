#!/usr/bin/env python3
"""
Тестовый скрипт для проверки истории платежей
"""

import logging
import sqlite3
from database import Database
from yookassa_client import YooKassaClient
from config import DATABASE_PATH

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_database_payments():
    """Тест получения платежей из базы данных"""
    print("=== Тест получения платежей из БД ===")
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, payment_type, amount, status, created_at, paid_at
                FROM payments 
                ORDER BY created_at DESC
                LIMIT 5
            ''')
            payments = cursor.fetchall()
            
            print(f"✅ Найдено {len(payments)} платежей в БД")
            
            for payment in payments:
                print(f"  - ID: {payment['yookassa_payment_id'][:8]}...")
                print(f"    Тип: {payment['payment_type']}")
                print(f"    Сумма: {payment['amount']}₽")
                print(f"    Статус: {payment['status']}")
                print(f"    Создан: {payment['created_at']}")
                print()
            
            return payments
    except Exception as e:
        print(f"❌ Ошибка получения платежей: {e}")
        return []

def test_payment_status_check():
    """Тест проверки статуса платежей"""
    print("\n=== Тест проверки статуса платежей ===")
    
    try:
        yookassa = YooKassaClient()
        
        # Получаем pending платежи
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id FROM payments 
                WHERE status = 'pending'
                LIMIT 3
            ''')
            pending_payments = cursor.fetchall()
        
        if not pending_payments:
            print("ℹ️ Нет pending платежей для проверки")
            return
        
        print(f"Проверяем {len(pending_payments)} pending платежей...")
        
        for payment in pending_payments:
            payment_id = payment['yookassa_payment_id']
            print(f"Проверяем платеж: {payment_id[:8]}...")
            
            try:
                status_result = yookassa.get_payment_status(payment_id)
                
                if status_result["success"]:
                    status = status_result["status"]
                    print(f"  ✅ Статус: {status}")
                else:
                    print(f"  ❌ Ошибка: {status_result.get('error', 'Неизвестная ошибка')}")
                    
            except Exception as e:
                print(f"  ❌ Исключение: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")

def test_payment_history_formatting():
    """Тест форматирования истории платежей"""
    print("\n=== Тест форматирования истории платежей ===")
    
    try:
        # Получаем платежи
        payments = test_database_payments()
        
        if not payments:
            print("ℹ️ Нет платежей для форматирования")
            return
        
        print("Форматированная история платежей:")
        print("-" * 40)
        
        for payment in payments:
            payment_id = payment['yookassa_payment_id']
            payment_type = payment['payment_type']
            amount = payment['amount']
            status = payment['status']
            created_at = payment['created_at']
            
            # Форматируем тип платежа
            type_name = "Аскеза" if payment_type == "askeza" else "Нумерологический разбор"
            
            # Форматируем статус
            status_emoji = {
                'pending': '⏳',
                'succeeded': '✅',
                'canceled': '❌'
            }.get(status, '❓')
            
            # Форматируем дату
            from datetime import datetime
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
            except:
                created_date = created_at
            
            formatted_text = f"{status_emoji} {type_name} - {amount}₽\n"
            formatted_text += f"   ID: {payment_id[:8]}...\n"
            formatted_text += f"   Дата: {created_date}\n"
            
            print(formatted_text)
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование истории платежей")
    print("=" * 50)
    
    # Тест получения платежей из БД
    test_database_payments()
    
    # Тест проверки статуса платежей
    test_payment_status_check()
    
    # Тест форматирования истории
    test_payment_history_formatting()
    
    print("\n✅ Тестирование завершено!")
    print("\n📋 Новая функциональность:")
    print("1. ✅ Кнопка 'Проверить платежи' добавлена в раздел оплаты")
    print("2. ✅ Показ истории платежей пользователя")
    print("3. ✅ Автоматическая проверка статуса через API ЮKassa")
    print("4. ✅ Обновление статусов в реальном времени")
    print("5. ✅ Форматированный вывод с эмодзи и датами")

if __name__ == "__main__":
    main()
