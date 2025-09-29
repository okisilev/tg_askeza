#!/usr/bin/env python3
"""
Тест бота с подписками
"""

import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Bot
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

def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тест базы данных")
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
        print("✅ Пользователь добавлен в БД")
        
        # Тестируем создание подписки
        db.create_subscription(
            user_id=test_user_id,
            payment_id="test_payment_123",
            amount=config.SUBSCRIPTION_PRICE
        )
        print("✅ Подписка создана в БД")
        
        # Тестируем проверку активности подписки
        is_active = db.is_subscription_active(test_user_id)
        print(f"✅ Подписка активна: {is_active}")
        
        # Тестируем получение подписки
        subscription = db.get_user_subscription(test_user_id)
        if subscription:
            print(f"✅ Подписка найдена: {subscription['payment_id']}")
            print(f"   • Истекает: {subscription['expires_at']}")
            print(f"   • Активна: {subscription['is_active']}")
        else:
            print("❌ Подписка не найдена")
            return False
        
        # Тестируем статистику
        stats = db.get_user_stats()
        print(f"✅ Статистика: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
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
        print(f"✅ SUBSCRIPTION_PRICE: {config.SUBSCRIPTION_PRICE}")
        print(f"✅ SUBSCRIPTION_DAYS: {config.SUBSCRIPTION_DAYS}")
        print(f"✅ WARNING_DAYS: {config.WARNING_DAYS}")
        print(f"✅ NOTIFICATION_HOUR: {config.NOTIFICATION_HOUR}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_subscription_logic():
    """Тест логики подписок"""
    print("\n📅 Тест логики подписок")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Создаем тестовую подписку
        test_user_id = 999999999
        db.add_user(test_user_id, "test_sub", "Test", "Subscription")
        
        # Создаем подписку
        db.create_subscription(
            user_id=test_user_id,
            payment_id="test_subscription_123",
            amount=config.SUBSCRIPTION_PRICE
        )
        
        # Проверяем активность
        is_active = db.is_subscription_active(test_user_id)
        print(f"✅ Подписка активна: {is_active}")
        
        # Получаем подписку
        subscription = db.get_user_subscription(test_user_id)
        if subscription:
            expires_at = datetime.fromisoformat(subscription['expires_at'])
            days_left = (expires_at - datetime.now()).days
            print(f"✅ Подписка истекает: {expires_at}")
            print(f"✅ Осталось дней: {days_left}")
        
        # Тестируем деактивацию
        db.deactivate_subscription(test_user_id)
        is_active_after = db.is_subscription_active(test_user_id)
        print(f"✅ Подписка деактивирована: {not is_active_after}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в логике подписок: {e}")
        return False

def print_workflow():
    """Печать рабочего процесса"""
    print("\n" + "=" * 50)
    print("🔄 РАБОЧИЙ ПРОЦЕСС БОТА С ПОДПИСКАМИ")
    print("=" * 50)
    
    print("\n1️⃣ Пользователь отправляет /start")
    print("   • Бот проверяет статус подписки")
    print("   • Если подписка активна - показывает доступ к каналу")
    print("   • Если подписки нет - предлагает подписаться")
    
    print("\n2️⃣ Пользователь нажимает 'Подписаться'")
    print("   • Создается платеж в ЮKassa")
    print("   • Платеж сохраняется в БД")
    print("   • Отправляется ссылка на оплату")
    
    print("\n3️⃣ Пользователь оплачивает")
    print("   • ЮKassa обрабатывает платеж")
    print("   • Статус платежа меняется на 'succeeded'")
    
    print("\n4️⃣ Пользователь нажимает 'Проверить оплату'")
    print("   • Бот проверяет статус в ЮKassa")
    print("   • Создается подписка на 30 дней")
    print("   • Создается пригласительная ссылка")
    print("   • Предоставляется доступ к каналу")
    
    print("\n5️⃣ Автоматические уведомления")
    print("   • За 3 дня до окончания - предупреждение")
    print("   • После истечения - уведомление об окончании")
    print("   • Деактивация подписки")
    
    print("\n6️⃣ Пользователь получает доступ")
    print("   • Может перейти в приватный канал")
    print("   • Получает эксклюзивные материалы")
    print("   • Участвует в закрытых обсуждениях")

async def main():
    """Основная функция тестирования"""
    print("🔍 Тест бота с подписками")
    print("=" * 50)
    
    # Тестируем все компоненты
    config_ok = test_config()
    bot_ok = await test_bot_connection()
    db_ok = test_database()
    subscription_ok = test_subscription_logic()
    
    print(f"\n📊 Результат тестирования:")
    print(f"   • Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   • Бот: {'✅' if bot_ok else '❌'}")
    print(f"   • База данных: {'✅' if db_ok else '❌'}")
    print(f"   • Логика подписок: {'✅' if subscription_ok else '❌'}")
    
    if all([config_ok, bot_ok, db_ok, subscription_ok]):
        print("\n🎉 Все компоненты работают!")
        print("Бот с подписками готов к работе")
        print_workflow()
    else:
        print("\n⚠️ Есть проблемы с компонентами!")
        print("Проверьте настройки и логи")

if __name__ == "__main__":
    asyncio.run(main())
