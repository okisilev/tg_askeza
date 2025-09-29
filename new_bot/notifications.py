#!/usr/bin/env python3
"""
Модуль для отправки уведомлений о подписках
"""

import asyncio
import logging
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, bot_token: str, db: Database):
        self.bot = Bot(token=bot_token)
        self.db = db
    
    async def send_expiring_notifications(self):
        """Отправка уведомлений о скором окончании подписки"""
        print("🔔 Проверка подписок, истекающих через 3 дня...")
        logger.info("Проверка подписок, истекающих через 3 дня...")
        
        try:
            expiring_subscriptions = self.db.get_expiring_subscriptions(config.WARNING_DAYS)
            
            for subscription in expiring_subscriptions:
                user_id = subscription['user_id']
                
                # Проверяем, не отправляли ли уже уведомление
                if self.db.was_notification_sent(user_id, 'expiring_warning', 1):
                    print(f"⚠️ Уведомление уже отправлено пользователю {user_id}")
                    continue
                
                try:
                    expires_at = datetime.fromisoformat(subscription['expires_at'])
                    days_left = (expires_at - datetime.now()).days
                    
                    keyboard = [
                        [InlineKeyboardButton(f"🔄 Продлить подписку ({config.SUBSCRIPTION_PRICE} руб.)", callback_data="subscribe")],
                        [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    message_text = config.SUBSCRIPTION_EXPIRING_MESSAGE.format(days=days_left)
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message_text,
                        reply_markup=reply_markup
                    )
                    
                    # Записываем отправку уведомления
                    self.db.add_notification(user_id, 'expiring_warning')
                    
                    print(f"✅ Уведомление об окончании подписки отправлено пользователю {user_id}")
                    logger.info(f"Уведомление об окончании подписки отправлено пользователю {user_id}")
                    
                except TelegramError as e:
                    print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
                    logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
                except Exception as e:
                    print(f"❌ Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")
                    logger.error(f"Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")
            
            print(f"✅ Проверка завершена. Обработано подписок: {len(expiring_subscriptions)}")
            logger.info(f"Проверка завершена. Обработано подписок: {len(expiring_subscriptions)}")
            
        except Exception as e:
            print(f"❌ Ошибка при проверке истекающих подписок: {e}")
            logger.error(f"Ошибка при проверке истекающих подписок: {e}")
    
    async def send_expired_notifications(self):
        """Отправка уведомлений об истекших подписках"""
        print("🔔 Проверка истекших подписок...")
        logger.info("Проверка истекших подписок...")
        
        try:
            expired_subscriptions = self.db.get_expired_subscriptions()
            
            for subscription in expired_subscriptions:
                user_id = subscription['user_id']
                
                # Проверяем, не отправляли ли уже уведомление
                if self.db.was_notification_sent(user_id, 'subscription_expired', 1):
                    print(f"⚠️ Уведомление об истечении уже отправлено пользователю {user_id}")
                    continue
                
                try:
                    keyboard = [
                        [InlineKeyboardButton(f"🔄 Продлить подписку ({config.SUBSCRIPTION_PRICE} руб.)", callback_data="subscribe")],
                        [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    message_text = config.SUBSCRIPTION_EXPIRED_MESSAGE
                    
                    await self.bot.send_message(
                        chat_id=user_id,
                        text=message_text,
                        reply_markup=reply_markup
                    )
                    
                    # Деактивируем подписку
                    self.db.deactivate_subscription(user_id)
                    
                    # Записываем отправку уведомления
                    self.db.add_notification(user_id, 'subscription_expired')
                    
                    print(f"✅ Уведомление об истечении подписки отправлено пользователю {user_id}")
                    logger.info(f"Уведомление об истечении подписки отправлено пользователю {user_id}")
                    
                except TelegramError as e:
                    print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
                    logger.error(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
                except Exception as e:
                    print(f"❌ Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")
                    logger.error(f"Неожиданная ошибка при отправке уведомления пользователю {user_id}: {e}")
            
            print(f"✅ Проверка завершена. Обработано подписок: {len(expired_subscriptions)}")
            logger.info(f"Проверка завершена. Обработано подписок: {len(expired_subscriptions)}")
            
        except Exception as e:
            print(f"❌ Ошибка при проверке истекших подписок: {e}")
            logger.error(f"Ошибка при проверке истекших подписок: {e}")
    
    async def send_daily_notifications(self):
        """Ежедневная отправка уведомлений"""
        print("🔔 Ежедневная проверка уведомлений...")
        logger.info("Ежедневная проверка уведомлений...")
        
        try:
            # Проверяем подписки, истекающие через 3 дня
            await self.send_expiring_notifications()
            
            # Проверяем истекшие подписки
            await self.send_expired_notifications()
            
            print("✅ Ежедневная проверка уведомлений завершена")
            logger.info("Ежедневная проверка уведомлений завершена")
            
        except Exception as e:
            print(f"❌ Ошибка при ежедневной проверке уведомлений: {e}")
            logger.error(f"Ошибка при ежедневной проверке уведомлений: {e}")

async def run_notifications():
    """Запуск системы уведомлений"""
    print("🚀 Запуск системы уведомлений...")
    
    db = Database()
    notification_service = NotificationService(config.BOT_TOKEN, db)
    
    try:
        await notification_service.bot.initialize()
        print("✅ Бот для уведомлений инициализирован")
        
        # Отправляем уведомления
        await notification_service.send_daily_notifications()
        
        print("✅ Система уведомлений завершила работу")
        
    except Exception as e:
        print(f"❌ Ошибка в системе уведомлений: {e}")
        logger.error(f"Ошибка в системе уведомлений: {e}")
    finally:
        await notification_service.bot.shutdown()

if __name__ == "__main__":
    asyncio.run(run_notifications())
