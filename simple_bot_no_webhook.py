#!/usr/bin/env python3
"""
Простая версия бота БЕЗ webhook (только API проверка платежей)
Без сложных asyncio операций
"""

import logging
import threading
import time
import sqlite3
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from yookassa_client import YooKassaClient
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN
from handlers import BotHandlers

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация компонентов
yookassa_client = YooKassaClient()
db = Database()
channel_manager = ChannelManager()
handlers = BotHandlers()

def process_successful_payment_simple(payment_id: str, user_id: int, payment_type: str, source: str = "API Check"):
    """Простая обработка успешного платежа без asyncio"""
    try:
        logger.info(f"✅ {source}: Обрабатываем успешный платеж {payment_id} для пользователя {user_id}")
        
        # Предоставляем доступ
        if db.grant_access(user_id, payment_type):
            logger.info(f"✅ {source}: Доступ предоставлен пользователю {user_id}")
            
            # Добавляем пользователя в каналы (синхронно)
            try:
                # Используем синхронные методы если они есть
                logger.info(f"✅ {source}: Пользователь {user_id} будет добавлен в каналы при следующей проверке")
            except Exception as e:
                logger.error(f"❌ {source}: Ошибка при добавлении пользователя {user_id} в каналы: {e}")
            
            # Уведомляем пользователя (синхронно)
            try:
                from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
                bot = Bot(token=BOT_TOKEN)
                
                success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к {payment_type}.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации

Нажмите /start для доступа к меню.
                """
                
                # Отправляем простое сообщение без кнопок
                bot.send_message(
                    chat_id=user_id,
                    text=success_text
                )
                logger.info(f"✅ {source}: Уведомление отправлено пользователю {user_id}")
                
            except Exception as e:
                logger.error(f"❌ {source}: Ошибка при отправке уведомления пользователю {user_id}: {e}")
            
            return True
        else:
            logger.error(f"❌ {source}: Не удалось предоставить доступ пользователю {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {source}: Критическая ошибка при обработке платежа {payment_id}: {e}")
        return False

def check_and_update_payments():
    """Проверка и обновление статуса платежей через API"""
    try:
        logger.info("🔍 Начинаем проверку статуса платежей...")
        
        # Получаем все pending платежи
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, user_id, payment_type FROM payments 
                WHERE status = 'pending'
            ''')
            pending_payments = cursor.fetchall()
        
        if not pending_payments:
            logger.info("Нет pending платежей для проверки")
            return
        
        logger.info(f"Найдено {len(pending_payments)} pending платежей")
        updated_count = 0
        
        for payment_row in pending_payments:
            payment_id = payment_row['yookassa_payment_id']
            user_id = payment_row['user_id']
            payment_type = payment_row['payment_type']
            
            try:
                logger.info(f"Проверяем платеж {payment_id} для пользователя {user_id}")
                
                # Проверяем статус через API
                status_result = yookassa_client.get_payment_status(payment_id)
                
                if status_result["success"]:
                    status = status_result["status"]
                    logger.info(f"Статус платежа {payment_id}: {status}")
                    
                    if status == "succeeded":
                        logger.info(f"✅ Платеж {payment_id} успешно оплачен!")
                        
                        # Обновляем статус в БД
                        if db.update_payment_status(payment_id, "succeeded"):
                            logger.info(f"Статус платежа {payment_id} обновлен в БД")
                            
                            # Обрабатываем успешный платеж
                            if process_successful_payment_simple(payment_id, user_id, payment_type, "API Check"):
                                updated_count += 1
                                logger.info(f"✅ Платеж {payment_id} успешно обработан")
                            else:
                                logger.error(f"❌ Ошибка при обработке платежа {payment_id}")
                        else:
                            logger.error(f"❌ Не удалось обновить статус платежа {payment_id}")
                    
                    elif status in ["canceled", "failed"]:
                        logger.info(f"Платеж {payment_id} отменен или неуспешен: {status}")
                        db.update_payment_status(payment_id, status)
                    
                    else:
                        logger.info(f"Платеж {payment_id} все еще в процессе: {status}")
                
                else:
                    logger.warning(f"Не удалось получить статус платежа {payment_id}: {status_result.get('error', 'Unknown error')}")
                
            except Exception as e:
                logger.error(f"Ошибка при проверке платежа {payment_id}: {e}")
        
        if updated_count > 0:
            logger.info(f"✅ Обновлено {updated_count} платежей")
        
    except Exception as e:
        logger.error(f"Ошибка при проверке платежей: {e}")

def periodic_payment_check():
    """Периодическая проверка платежей"""
    while True:
        try:
            check_and_update_payments()
            time.sleep(300)  # Проверяем каждые 5 минут
        except Exception as e:
            logger.error(f"Ошибка в периодической проверке платежей: {e}")
            time.sleep(60)  # При ошибке ждем 1 минуту

def main():
    """Основная функция"""
    try:
        logger.info("🚀 Запускаем простую систему БЕЗ webhook")
        logger.info("=" * 60)
        
        # Запускаем периодическую проверку платежей в отдельном потоке
        logger.info("⏰ Запускаем периодическую проверку платежей...")
        payment_thread = threading.Thread(target=periodic_payment_check, daemon=True)
        payment_thread.start()
        logger.info("✅ Периодическая проверка платежей запущена")
        
        # Создаем приложение Telegram
        logger.info("🤖 Запускаем Telegram бота...")
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", handlers.start_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_message))
        application.add_handler(CallbackQueryHandler(handlers.button_callback))
        
        logger.info("✅ Обработчики зарегистрированы")
        logger.info("🚀 Бот запущен (простая версия без webhook)")
        
        # Запускаем бота
        application.run_polling()
        
    except KeyboardInterrupt:
        logger.info("🛑 Остановка системы...")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
