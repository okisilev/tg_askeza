#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы платежей ЮKassa
"""

import asyncio
import logging
from yookassa_client import YooKassaClient
from database import Database
from config import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_payment_creation():
    """Тест создания платежа"""
    print("=== Тест создания платежа ===")
    
    # Проверяем конфигурацию
    print(f"YOOKASSA_SHOP_ID: {YOOKASSA_SHOP_ID}")
    print(f"YOOKASSA_SECRET_KEY: {YOOKASSA_SECRET_KEY[:20]}...")
    
    # Создаем клиент ЮKassa
    yookassa = YooKassaClient()
    
    # Тестируем создание платежа для Аскезы
    print("\n--- Тест платежа Аскезы ---")
    result = yookassa.create_payment(
        amount=1000.0,
        description="Тестовый платеж для Аскезы",
        return_url="https://t.me/test_bot"
    )
    
    print(f"Результат создания платежа: {result}")
    
    if result["success"]:
        payment_id = result["payment_id"]
        print(f"ID платежа: {payment_id}")
        print(f"URL для оплаты: {result['confirmation_url']}")
        
        # Тестируем получение статуса платежа
        print("\n--- Тест получения статуса платежа ---")
        status_result = yookassa.get_payment_status(payment_id)
        print(f"Статус платежа: {status_result}")
    
    return result

async def test_database():
    """Тест работы с базой данных"""
    print("\n=== Тест базы данных ===")
    
    db = Database()
    
    # Тестируем добавление пользователя
    print("--- Тест добавления пользователя ---")
    user_added = db.add_user(
        user_id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    print(f"Пользователь добавлен: {user_added}")
    
    # Тестируем создание платежа
    print("--- Тест создания платежа в БД ---")
    payment_created = db.create_payment(
        user_id=123456789,
        payment_type="askeza",
        amount=1000.0,
        yookassa_payment_id="test_payment_123"
    )
    print(f"Платеж создан: {payment_created}")
    
    # Тестируем получение платежа
    print("--- Тест получения платежа ---")
    payment = db.get_payment("test_payment_123")
    print(f"Платеж получен: {payment}")
    
    # Тестируем обновление статуса
    print("--- Тест обновления статуса ---")
    status_updated = db.update_payment_status("test_payment_123", "succeeded")
    print(f"Статус обновлен: {status_updated}")
    
    # Тестируем предоставление доступа
    print("--- Тест предоставления доступа ---")
    access_granted = db.grant_access(123456789, "askeza")
    print(f"Доступ предоставлен: {access_granted}")
    
    # Тестируем получение доступа пользователя
    print("--- Тест получения доступа пользователя ---")
    user_access = db.get_user_access(123456789)
    print(f"Доступ пользователя: {user_access}")

async def test_webhook_processing():
    """Тест обработки webhook"""
    print("\n=== Тест обработки webhook ===")
    
    yookassa = YooKassaClient()
    
    # Симулируем webhook данные (упрощенные)
    webhook_data = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": "test_payment_123",
            "status": "succeeded",
            "amount": {
                "value": "1000.00",
                "currency": "RUB"
            },
            "metadata": {}
        }
    }
    
    print("--- Тест обработки webhook ---")
    result = yookassa.process_webhook(webhook_data)
    print(f"Результат обработки webhook: {result}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов бота Аскезы")
    print("=" * 50)
    
    try:
        # Тест создания платежа
        await test_payment_creation()
        
        # Тест базы данных
        await test_database()
        
        # Тест обработки webhook
        await test_webhook_processing()
        
        print("\n✅ Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        logger.error(f"Ошибка в тестах: {e}")

if __name__ == "__main__":
    asyncio.run(main())
