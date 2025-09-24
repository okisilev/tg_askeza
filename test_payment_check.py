#!/usr/bin/env python3
"""
Тестовый скрипт для проверки автоматической проверки платежей
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

def test_database_connection():
    """Тест подключения к базе данных"""
    print("=== Тест подключения к БД ===")
    
    try:
        db = Database()
        print("✅ База данных инициализирована")
        
        # Проверяем таблицы
        with sqlite3.connect(db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"✅ Таблицы в БД: {[table[0] for table in tables]}")
            
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к БД: {e}")
        return False

def test_pending_payments():
    """Тест получения pending платежей"""
    print("\n=== Тест получения pending платежей ===")
    
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, user_id, payment_type FROM payments 
                WHERE status = 'pending'
            ''')
            pending_payments = cursor.fetchall()
            
            print(f"✅ Найдено {len(pending_payments)} pending платежей")
            
            for payment in pending_payments:
                print(f"  - ID: {payment['yookassa_payment_id']}, User: {payment['user_id']}, Type: {payment['payment_type']}")
            
            return pending_payments
    except Exception as e:
        print(f"❌ Ошибка получения pending платежей: {e}")
        return []

def test_yookassa_connection():
    """Тест подключения к ЮKassa"""
    print("\n=== Тест подключения к ЮKassa ===")
    
    try:
        yookassa = YooKassaClient()
        print("✅ ЮKassa клиент инициализирован")
        
        # Тестируем создание тестового платежа
        result = yookassa.create_payment(
            amount=990.0,
            description="Тестовый платеж",
            return_url="https://t.me/test_bot"
        )
        
        if result["success"]:
            print(f"✅ Тестовый платеж создан: {result['payment_id']}")
            
            # Тестируем получение статуса
            status_result = yookassa.get_payment_status(result["payment_id"])
            print(f"✅ Статус платежа: {status_result}")
            
            return True
        else:
            print(f"❌ Ошибка создания тестового платежа: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к ЮKassa: {e}")
        return False

def test_payment_status_check():
    """Тест проверки статуса платежа"""
    print("\n=== Тест проверки статуса платежа ===")
    
    try:
        yookassa = YooKassaClient()
        
        # Получаем pending платежи
        pending_payments = test_pending_payments()
        
        if not pending_payments:
            print("ℹ️ Нет pending платежей для проверки")
            return True
        
        # Проверяем первый pending платеж
        payment = pending_payments[0]
        payment_id = payment['yookassa_payment_id']
        
        print(f"Проверяем платеж: {payment_id}")
        
        status_result = yookassa.get_payment_status(payment_id)
        
        if status_result["success"]:
            print(f"✅ Статус платежа {payment_id}: {status_result['status']}")
            return True
        else:
            print(f"❌ Ошибка получения статуса: {status_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка проверки статуса: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование автоматической проверки платежей")
    print("=" * 60)
    
    # Тест подключения к БД
    if not test_database_connection():
        print("❌ Критическая ошибка: не удалось подключиться к БД")
        return
    
    # Тест подключения к ЮKassa
    if not test_yookassa_connection():
        print("❌ Критическая ошибка: не удалось подключиться к ЮKassa")
        return
    
    # Тест получения pending платежей
    test_pending_payments()
    
    # Тест проверки статуса
    test_payment_status_check()
    
    print("\n✅ Тестирование завершено!")
    print("\n📋 Рекомендации:")
    print("1. Убедитесь, что webhook настроен в ЮKassa")
    print("2. Проверьте, что сервер доступен из интернета")
    print("3. Запустите main.py для полной работы системы")

if __name__ == "__main__":
    main()
