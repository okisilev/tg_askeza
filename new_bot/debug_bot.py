#!/usr/bin/env python3
"""
Диагностика проблем с ботом
"""

import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_bot_connection():
    """Тест подключения к боту"""
    print("🤖 Тест подключения к боту")
    print("=" * 50)
    
    try:
        bot = Bot(token=config.BOT_TOKEN)
        await bot.initialize()
        
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"   • ID: {bot_info.id}")
        print(f"   • Имя: {bot_info.first_name}")
        print(f"   • Username: @{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False

def test_database_connection():
    """Тест подключения к базе данных"""
    print("\n💾 Тест подключения к базе данных")
    print("=" * 50)
    
    try:
        db = Database()
        print("✅ База данных подключена")
        
        # Тестируем добавление пользователя
        test_user_id = 999999999
        db.add_user(
            user_id=test_user_id,
            username="debug_user",
            first_name="Debug",
            last_name="User"
        )
        print("✅ Пользователь добавлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n⚙️ Тест конфигурации")
    print("=" * 50)
    
    try:
        print(f"✅ BOT_TOKEN: {config.BOT_TOKEN[:10]}...")
        print(f"✅ YOOKASSA_SHOP_ID: {config.YOOKASSA_SHOP_ID}")
        print(f"✅ YOOKASSA_SECRET_KEY: {config.YOOKASSA_SECRET_KEY[:10]}...")
        print(f"✅ PRIVATE_CHANNEL_ID: {config.PRIVATE_CHANNEL_ID}")
        print(f"✅ PAYMENT_AMOUNT: {config.PAYMENT_AMOUNT}")
        print(f"✅ PAYMENT_DESCRIPTION: {config.PAYMENT_DESCRIPTION}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

async def test_payment_creation():
    """Тест создания платежа"""
    print("\n💳 Тест создания платежа")
    print("=" * 50)
    
    try:
        from yookassa import Configuration, Payment
        from yookassa.domain.request import PaymentRequest
        import uuid
        
        # Инициализация ЮKassa
        Configuration.account_id = config.YOOKASSA_SHOP_ID
        Configuration.secret_key = config.YOOKASSA_SECRET_KEY
        
        # Создаем тестовый платеж
        payment_id = str(uuid.uuid4())
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
            "description": "Тестовый платеж",
            "capture": True
        })
        
        payment = Payment.create(payment_request, payment_id)
        print(f"✅ Платеж создан: {payment.id}")
        print(f"✅ Статус: {payment.status}")
        print(f"✅ URL: {payment.confirmation.confirmation_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании платежа: {e}")
        return False

def test_handlers():
    """Тест обработчиков"""
    print("\n🔧 Тест обработчиков")
    print("=" * 50)
    
    try:
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Проверяем, что обработчики добавлены
        handlers = application.handlers[0]
        print(f"✅ Обработчиков зарегистрировано: {len(handlers)}")
        
        for handler in handlers:
            print(f"   • {type(handler).__name__}: {handler.pattern if hasattr(handler, 'pattern') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании обработчиков: {e}")
        return False

def print_troubleshooting():
    """Печать рекомендаций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 РЕКОМЕНДАЦИИ ПО УСТРАНЕНИЮ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте, что бот запущен:")
    print("   python bot.py")
    
    print("\n2️⃣ Проверьте логи на ошибки:")
    print("   • Ищите ошибки при создании платежей")
    print("   • Проверьте ошибки при работе с базой данных")
    print("   • Убедитесь, что ЮKassa API работает")
    
    print("\n3️⃣ Проверьте настройки:")
    print("   • BOT_TOKEN настроен правильно")
    print("   • YOOKASSA_SHOP_ID и YOOKASSA_SECRET_KEY настроены")
    print("   • База данных доступна")
    
    print("\n4️⃣ Перезапустите бота:")
    print("   • Остановите бота (Ctrl+C)")
    print("   • Запустите заново: python bot.py")
    
    print("\n5️⃣ Проверьте права бота:")
    print("   • Бот должен быть администратором канала")
    print("   • У бота должны быть права на приглашение")

async def main():
    """Основная функция диагностики"""
    print("🔍 Диагностика проблем с ботом")
    print("=" * 50)
    
    # Тестируем все компоненты
    config_ok = test_config()
    db_ok = test_database_connection()
    bot_ok = await test_bot_connection()
    payment_ok = await test_payment_creation()
    handlers_ok = test_handlers()
    
    print(f"\n📊 Результат диагностики:")
    print(f"   • Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   • База данных: {'✅' if db_ok else '❌'}")
    print(f"   • Бот: {'✅' if bot_ok else '❌'}")
    print(f"   • Платежи: {'✅' if payment_ok else '❌'}")
    print(f"   • Обработчики: {'✅' if handlers_ok else '❌'}")
    
    if all([config_ok, db_ok, bot_ok, payment_ok, handlers_ok]):
        print("\n🎉 Все компоненты работают!")
        print("Проблема может быть в том, что бот не запущен")
        print("Запустите бота: python bot.py")
    else:
        print("\n⚠️ Есть проблемы с компонентами!")
        print("Проверьте настройки и логи")
    
    # Показываем рекомендации
    print_troubleshooting()

if __name__ == "__main__":
    asyncio.run(main())
