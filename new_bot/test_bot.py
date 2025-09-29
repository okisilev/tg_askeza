#!/usr/bin/env python3
"""
Тестирование бота с ЮKassa API
"""

import asyncio
import logging
from config import config
from database import Database
from yookassa import Configuration, Payment
from yookassa.domain.request import PaymentRequest
from yookassa.domain.response import PaymentResponse

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация ЮKassa
Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY

def test_database():
    """Тест базы данных"""
    print("🧪 Тестирование базы данных")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Тестируем добавление пользователя
        test_user_id = 123456789
        db.add_user(
            user_id=test_user_id,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        print("✅ Пользователь добавлен в базу данных")
        
        # Тестируем добавление платежа с уникальным ID
        import uuid
        test_payment_id = f"test_payment_{uuid.uuid4()}"
        db.add_payment(
            user_id=test_user_id,
            payment_id=test_payment_id,
            amount=config.PAYMENT_AMOUNT
        )
        print("✅ Платеж добавлен в базу данных")
        
        # Тестируем получение платежа
        payment_info = db.get_user_payment(test_user_id)
        if payment_info:
            print(f"✅ Платеж найден: {payment_info['payment_id']}")
        else:
            print("❌ Платеж не найден")
        
        # Тестируем обновление статуса
        db.update_payment_status(test_payment_id, "succeeded")
        print("✅ Статус платежа обновлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании базы данных: {e}")
        return False

def test_yookassa_connection():
    """Тест подключения к ЮKassa"""
    print("\n🧪 Тестирование подключения к ЮKassa")
    print("=" * 50)
    
    try:
        # Проверяем конфигурацию
        print(f"✅ Shop ID: {Configuration.account_id}")
        print(f"✅ Secret Key: {Configuration.secret_key[:10]}...")
        
        # Тестируем создание платежа
        test_payment_id = "test_payment_456"
        payment_request = PaymentRequest({
            "amount": {
                "value": "1.00",  # Тестовая сумма
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/test"
            },
            "description": "Тестовый платеж",
            "capture": True
        })
        
        payment = Payment.create(payment_request, test_payment_id)
        
        print(f"✅ Платеж создан: {payment.id}")
        print(f"✅ Статус: {payment.status}")
        print(f"✅ URL: {payment.confirmation.confirmation_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании ЮKassa: {e}")
        return False

def test_payment_status():
    """Тест проверки статуса платежа"""
    print("\n🧪 Тестирование проверки статуса платежа")
    print("=" * 50)
    
    try:
        # Создаем тестовый платеж
        import uuid
        test_payment_id = str(uuid.uuid4())
        payment_request = PaymentRequest({
            "amount": {
                "value": "1.00",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/test"
            },
            "description": "Тестовый платеж для проверки статуса",
            "capture": True
        })
        
        payment = Payment.create(payment_request, test_payment_id)
        print(f"✅ Платеж создан: {payment.id}")
        
        # Проверяем статус
        payment_info = Payment.find_one(payment.id)  # Используем реальный ID платежа
        print(f"✅ Статус платежа: {payment_info.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке статуса платежа: {e}")
        return False

def print_config_info():
    """Печать информации о конфигурации"""
    print("\n📋 Информация о конфигурации")
    print("=" * 50)
    
    print(f"🤖 BOT_TOKEN: {config.BOT_TOKEN[:10]}...")
    print(f"🏪 YOOKASSA_SHOP_ID: {config.YOOKASSA_SHOP_ID}")
    print(f"🔑 YOOKASSA_SECRET_KEY: {config.YOOKASSA_SECRET_KEY[:10]}...")
    print(f"📺 PRIVATE_CHANNEL_ID: {config.PRIVATE_CHANNEL_ID}")
    print(f"💰 PAYMENT_AMOUNT: {config.PAYMENT_AMOUNT} рублей")
    print(f"📝 PAYMENT_DESCRIPTION: {config.PAYMENT_DESCRIPTION}")

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование бота с ЮKassa API")
    print("=" * 50)
    
    # Показываем информацию о конфигурации
    print_config_info()
    
    # Тестируем базу данных
    db_ok = test_database()
    
    # Тестируем подключение к ЮKassa
    yookassa_ok = test_yookassa_connection()
    
    # Тестируем проверку статуса платежа
    status_ok = test_payment_status()
    
    print(f"\n📊 Результат тестирования:")
    print(f"   • База данных: {'✅' if db_ok else '❌'}")
    print(f"   • ЮKassa: {'✅' if yookassa_ok else '❌'}")
    print(f"   • Статус платежа: {'✅' if status_ok else '❌'}")
    
    if db_ok and yookassa_ok and status_ok:
        print("\n🎉 Все тесты пройдены успешно!")
        print("Бот готов к запуску: python bot.py")
    else:
        print("\n⚠️ Есть проблемы с настройкой!")
        print("Проверьте конфигурацию и логи")

if __name__ == "__main__":
    main()
