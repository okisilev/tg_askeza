#!/usr/bin/env python3
"""
Основная программа для запуска бота и webhook сервера
"""

import asyncio
import logging
import threading
import time
from flask import Flask, request, jsonify
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from yookassa_client import YooKassaClient
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN, YOOKASSA_SECRET_KEY
import json

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
bot = Bot(token=BOT_TOKEN)

# Flask приложение для webhook
app = Flask(__name__)

# Импортируем обработчики из handlers.py
from handlers import BotHandlers
from callback_handler import callback_handler
handlers = BotHandlers()

# Создаем простой обработчик callback'ов для main.py
async def handle_callback_in_main(callback_data: str, user_id: int):
    """Обработка callback'ов в main.py"""
    try:
        logger.info(f"Обрабатываем callback в main.py: {callback_data} для пользователя {user_id}")
        
        if callback_data == "private_channel":
            await callback_handler.give_channel_access(user_id)
        elif callback_data == "private_chat":
            await callback_handler.give_chat_access(user_id)
        elif callback_data == "back_to_main":
            await callback_handler.show_main_menu(user_id)
        else:
            logger.warning(f"Неизвестный callback в main.py: {callback_data}")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке callback в main.py: {e}")

def process_successful_payment(payment_id: str, user_id: int, payment_type: str, source: str = "unknown"):
    """Обработка успешного платежа"""
    try:
        logger.info(f"✅ {source}: Обрабатываем успешный платеж {payment_id} для пользователя {user_id}")
        
        # Предоставляем доступ
        if db.grant_access(user_id, payment_type):
            logger.info(f"✅ {source}: Доступ предоставлен пользователю {user_id}")
            
            # Добавляем пользователя в каналы
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(
                    channel_manager.grant_access_to_user(user_id, payment_type)
                )
                loop.close()
                
                if success:
                    logger.info(f"✅ {source}: Пользователь {user_id} добавлен в каналы")
                else:
                    logger.warning(f"⚠️ {source}: Не удалось добавить пользователя {user_id} в каналы")
                    
            except Exception as e:
                logger.error(f"❌ {source}: Ошибка при добавлении пользователя {user_id} в каналы: {e}")
            
            # Уведомляем пользователя
            try:
                success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к {payment_type}.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
                """
                
                keyboard = [
                    [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                    [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(bot.send_message(
                    chat_id=user_id,
                    text=success_text,
                    reply_markup=reply_markup
                ))
                loop.close()
                logger.info(f"✅ {source}: Уведомление отправлено пользователю {user_id}")
                
            except Exception as e:
                logger.error(f"❌ {source}: Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            return True
        else:
            logger.error(f"❌ {source}: Не удалось предоставить доступ пользователю {user_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ {source}: Критическая ошибка при обработке платежа {payment_id}: {e}")
        return False

@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    """Обработка webhook от ЮKassa"""
    try:
        # Получаем данные из webhook
        webhook_data = request.get_json()
        
        if not webhook_data:
            logger.error("Пустые данные webhook")
            return jsonify({"error": "Empty data"}), 400
        
        logger.info(f"Получен webhook: {webhook_data}")
        
        # Обрабатываем webhook через YooKassa клиент
        result = yookassa_client.process_webhook(webhook_data)
        
        if result["success"] and result.get("status") == "succeeded":
            payment_id = result["payment_id"]
            logger.info(f"✅ Webhook: Платеж {payment_id} успешно обработан")
            
            # Обновляем статус платежа в базе данных
            if db.update_payment_status(payment_id, "succeeded"):
                logger.info(f"✅ Webhook: Статус платежа {payment_id} обновлен в БД")
                
                # Получаем информацию о платеже
                payment_info = db.get_payment(payment_id)
                if payment_info:
                    user_id = payment_info["user_id"]
                    payment_type = payment_info["payment_type"]
                    
                    # Обрабатываем успешный платеж
                    process_successful_payment(payment_id, user_id, payment_type, "Webhook")
                else:
                    logger.error(f"❌ Webhook: Не удалось получить информацию о платеже {payment_id}")
            else:
                logger.error(f"❌ Webhook: Не удалось обновить статус платежа {payment_id}")
        else:
            logger.warning(f"⚠️ Webhook: Платеж не успешен или ошибка обработки: {result}")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "healthy"})

def check_and_update_payments():
    """Проверка и обновление статуса платежей через API"""
    try:
        logger.info("🔍 Начинаем проверку статуса платежей...")
        
        # Получаем все pending платежи
        import sqlite3
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
                            if process_successful_payment(payment_id, user_id, payment_type, "API Check"):
                                updated_count += 1
                            else:
                                logger.error(f"❌ Не удалось обработать успешный платеж {payment_id}")
                        else:
                            logger.error(f"❌ Не удалось обновить статус платежа {payment_id}")
                    
                    elif status == "canceled":
                        logger.info(f"❌ Платеж {payment_id} отменен")
                        db.update_payment_status(payment_id, "canceled")
                    
                    elif status == "pending":
                        logger.info(f"⏳ Платеж {payment_id} все еще в обработке")
                    
                    else:
                        logger.warning(f"⚠️ Неизвестный статус платежа {payment_id}: {status}")
                
                else:
                    logger.error(f"❌ Ошибка при получении статуса платежа {payment_id}: {status_result.get('error', 'Неизвестная ошибка')}")
                
            except Exception as e:
                logger.error(f"❌ Ошибка при проверке платежа {payment_id}: {e}")
        
        if updated_count > 0:
            logger.info(f"✅ Обновлено {updated_count} платежей")
        else:
            logger.info("ℹ️ Нет платежей для обновления")
        
    except Exception as e:
        logger.error(f"❌ Критическая ошибка при проверке платежей: {e}")

def periodic_payment_check():
    """Периодическая проверка платежей"""
    logger.info("🔄 Запуск периодической проверки платежей")
    
    while True:
        try:
            logger.info("⏰ Начинаем периодическую проверку...")
            check_and_update_payments()
            logger.info("✅ Периодическая проверка завершена")
            time.sleep(300)  # Проверяем каждые 5 минут
        except KeyboardInterrupt:
            logger.info("🛑 Периодическая проверка остановлена пользователем")
            break
        except Exception as e:
            logger.error(f"❌ Ошибка в периодической проверке: {e}")
            logger.info("⏳ Ждем 60 секунд перед следующей попыткой...")
            time.sleep(60)  # При ошибке ждем минуту

def start_webhook_server():
    """Запуск webhook сервера"""
    logger.info("🚀 Запуск webhook сервера на порту 5000")
    logger.info("📡 Webhook URL: http://localhost:5000/webhook/yookassa")
    logger.info("🏥 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=5000, debug=False)

def start_bot():
    """Запуск Telegram бота"""
    from bot import AskezaBot
    
    logger.info("🤖 Запуск Telegram бота Аскезы")
    
    try:
        bot_instance = AskezaBot()
        bot_instance.run()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")

if __name__ == "__main__":
    logger.info("🚀 Запуск основной программы")
    
    # Запускаем периодическую проверку платежей в отдельном потоке
    payment_check_thread = threading.Thread(target=periodic_payment_check, daemon=True)
    payment_check_thread.start()
    logger.info("✅ Запущена периодическая проверка платежей")
    
    # Запускаем webhook сервер в отдельном потоке
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()
    logger.info("✅ Запущен webhook сервер")
    
    # Запускаем бота в основном потоке
    start_bot()
