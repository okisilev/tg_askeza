import logging
from flask import Flask, request, jsonify
from yookassa_client import YooKassaClient
from database import Database
from channel_manager import ChannelManager
from telegram import Bot
from config import BOT_TOKEN, YOOKASSA_SECRET_KEY
import json

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Инициализация компонентов
yookassa_client = YooKassaClient()
db = Database()
channel_manager = ChannelManager()
bot = Bot(token=BOT_TOKEN)

@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    """Обработка webhook от ЮKassa"""
    try:
        # Получаем данные из webhook
        webhook_data = request.get_json()
        
        if not webhook_data:
            logger.error("Пустые данные webhook")
            return jsonify({"error": "Empty data"}), 400
        
        # Обрабатываем webhook через YooKassa клиент
        result = yookassa_client.process_webhook(webhook_data)
        
        if result["success"] and result.get("status") == "succeeded":
            payment_id = result["payment_id"]
            
            # Обновляем статус платежа в базе данных
            db.update_payment_status(payment_id, "succeeded")
            
            # Получаем информацию о платеже
            payment_info = db.get_payment(payment_id)
            if payment_info:
                user_id = payment_info["user_id"]
                payment_type = payment_info["payment_type"]
                
                # Предоставляем доступ
                db.grant_access(user_id, payment_type)
                
                # Добавляем пользователя в каналы
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(channel_manager.grant_access_to_user(user_id, payment_type))
                loop.close()
                
                # Уведомляем пользователя
                success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к {payment_type}.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
                """
                
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                keyboard = [
                    [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                    [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Отправляем уведомление пользователю
                try:
                    bot.send_message(
                        chat_id=user_id,
                        text=success_text,
                        reply_markup=reply_markup
                    )
                    logger.info(f"Уведомление отправлено пользователю {user_id}")
                except Exception as e:
                    logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Ошибка при обработке webhook: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Проверка здоровья сервера"""
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
