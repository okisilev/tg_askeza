#!/usr/bin/env python3
"""
Тест успешной оплаты и создания пригласительной ссылки
"""

import asyncio
import logging
from telegram import Bot
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_successful_payment():
    """Тестирует успешную оплату и создание пригласительной ссылки"""
    
    print("🔍 Тестирование успешной оплаты...")
    
    try:
        # Создаем бота
        bot = Bot(token=config.BOT_TOKEN)
        await bot.initialize()
        print("✅ Бот инициализирован")
        
        # Инициализируем базу данных
        db = Database()
        print("✅ База данных инициализирована")
        
        # Тестовые данные
        test_user_id = 431292182
        test_payment_id = "test_payment_123"
        test_amount = config.SUBSCRIPTION_PRICE
        
        print(f"👤 Тестовый пользователь: {test_user_id}")
        print(f"💰 Сумма: {test_amount} рублей")
        print(f"🆔 Payment ID: {test_payment_id}")
        
        # Создаем подписку
        try:
            db.create_subscription(test_user_id, test_payment_id, test_amount)
            print("✅ Подписка создана в базе данных")
        except Exception as e:
            print(f"❌ Ошибка при создании подписки: {e}")
            return
        
        # Создаем пригласительную ссылку
        try:
            print("🔗 Создаем пригласительную ссылку...")
            invite_link = await bot.create_chat_invite_link(
                chat_id=int(config.PRIVATE_CHANNEL_ID),
                member_limit=1,
                expire_date=None
            )
            print(f"✅ Пригласительная ссылка создана: {invite_link.invite_link}")
            
            # Отправляем уведомление пользователю
            user_notification = f"""
🎉 **Поздравляем! Оплата прошла успешно!**

💰 **Сумма:** {config.SUBSCRIPTION_PRICE} рублей
📅 **Подписка:** {config.SUBSCRIPTION_DAYS} дней
⏰ **Активна до:** {(datetime.now() + timedelta(days=config.SUBSCRIPTION_DAYS)).strftime('%d.%m.%Y %H:%M')}

✅ **Ваш доступ к закрытому каналу активирован!**

🔗 **Ссылка для входа в канал:**
{invite_link.invite_link}
            """
            
            await bot.send_message(
                chat_id=test_user_id,
                text=user_notification
            )
            print("✅ Уведомление пользователю отправлено")
            
            # Отправляем уведомление админу
            admin_notification = f"""
🔔 **Новая успешная оплата!**

👤 **Пользователь:** Тестовый пользователь
🆔 **ID:** {test_user_id}
📱 **Username:** @test_user
💰 **Сумма:** {config.SUBSCRIPTION_PRICE} рублей
📅 **Подписка:** {config.SUBSCRIPTION_DAYS} дней
🆔 **Payment ID:** {test_payment_id}
⏰ **Время:** {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
            """
            
            await bot.send_message(
                chat_id=config.ADMIN_ID,
                text=admin_notification
            )
            print("✅ Уведомление админу отправлено")
            
        except Exception as e:
            print(f"❌ Ошибка при создании пригласительной ссылки: {e}")
            return
        
        print("✅ Тест успешной оплаты завершен!")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        logger.error(f"Общая ошибка: {e}")
    finally:
        try:
            await bot.shutdown()
            print("✅ Бот закрыт")
        except:
            pass

if __name__ == "__main__":
    from datetime import datetime, timedelta
    asyncio.run(test_successful_payment())
