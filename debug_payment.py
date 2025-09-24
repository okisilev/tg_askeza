#!/usr/bin/env python3
"""
Отладочный скрипт для проверки работы платежей
"""

import logging
from yookassa_client import YooKassaClient
from config import YOOKASSA_SECRET_KEY, YOOKASSA_SHOP_ID, ASKEZA_PRICE, NUMEROLOGY_PRICE

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_config():
    """Проверка конфигурации"""
    print("=== Проверка конфигурации ===")
    print(f"YOOKASSA_SHOP_ID: {YOOKASSA_SHOP_ID}")
    print(f"YOOKASSA_SECRET_KEY: {YOOKASSA_SECRET_KEY[:20]}...")
    print(f"ASKEZA_PRICE: {ASKEZA_PRICE}")
    print(f"NUMEROLOGY_PRICE: {NUMEROLOGY_PRICE}")

def test_payment_amounts():
    """Тест получения сумм платежей"""
    print("\n=== Тест получения сумм платежей ===")
    
    yookassa = YooKassaClient()
    
    # Тест Аскезы
    try:
        askeza_amount = yookassa.get_payment_amount("askeza")
        askeza_description = yookassa.get_payment_description("askeza")
        print(f"✅ Аскеза: {askeza_amount}₽ - {askeza_description}")
    except Exception as e:
        print(f"❌ Ошибка для Аскезы: {e}")
    
    # Тест Нумерологии
    try:
        numerology_amount = yookassa.get_payment_amount("numerology")
        numerology_description = yookassa.get_payment_description("numerology")
        print(f"✅ Нумерология: {numerology_amount}₽ - {numerology_description}")
    except Exception as e:
        print(f"❌ Ошибка для Нумерологии: {e}")

def test_payment_creation():
    """Тест создания платежа"""
    print("\n=== Тест создания платежа ===")
    
    yookassa = YooKassaClient()
    
    # Тест создания платежа для Нумерологии
    try:
        print("Создаем платеж для нумерологии...")
        result = yookassa.create_payment(
            amount=2490.0,
            description="Тестовый платеж для Нумерологии",
            return_url="https://t.me/test_bot"
        )
        
        if result["success"]:
            print(f"✅ Платеж создан успешно")
            print(f"ID: {result['payment_id']}")
            print(f"URL: {result['confirmation_url']}")
        else:
            print(f"❌ Ошибка: {result.get('error', 'Неизвестная ошибка')}")
            
    except Exception as e:
        print(f"❌ Исключение при создании платежа: {e}")

def main():
    """Основная функция тестирования"""
    print("🔍 Отладка платежей")
    print("=" * 50)
    
    test_config()
    test_payment_amounts()
    test_payment_creation()
    
    print("\n✅ Отладка завершена!")

if __name__ == "__main__":
    main()
