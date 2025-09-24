
import logging
import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from config import BOT_TOKEN, YOOKASSA_SECRET_KEY
from handlers import BotHandlers
from database import Database
from channel_manager import ChannelManager
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AskezaBot:
    def __init__(self):
        self.handlers = BotHandlers()
        self.db = Database()
        self.channel_manager = ChannelManager()
    
    async def debug_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик для отладки callback'ов"""
        logger.info(f"DEBUG CALLBACK: Получен callback от пользователя {update.callback_query.from_user.id}")
        logger.info(f"DEBUG CALLBACK: Данные: {update.callback_query.data}")
        # Не обрабатываем callback, просто логируем
    
    async def webhook_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик webhook от ЮKassa"""
        try:
            # Получаем данные из webhook
            if update.message:
                webhook_data = update.message.text
            else:
                webhook_data = str(update)
            
            # Парсим JSON данные
            try:
                webhook_json = json.loads(webhook_data)
            except json.JSONDecodeError:
                logger.error("Не удалось распарсить JSON из webhook")
                return
            
            # Обрабатываем webhook через YooKassa клиент
            result = self.handlers.yookassa.process_webhook(webhook_json)
            
            if result["success"] and result.get("status") == "succeeded":
                payment_id = result["payment_id"]
                
                # Обновляем статус платежа в базе данных
                self.db.update_payment_status(payment_id, "succeeded")
                
                # Получаем информацию о платеже
                payment_info = self.db.get_payment(payment_id)
                if payment_info:
                    user_id = payment_info["user_id"]
                    payment_type = payment_info["payment_type"]
                    
                    # Предоставляем доступ
                    self.db.grant_access(user_id, payment_type)
                    
                    # Добавляем пользователя в каналы
                    await self.channel_manager.grant_access_to_user(user_id, payment_type)
                    
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
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=success_text,
                        reply_markup=reply_markup
                    )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {e}")
    
    async def cleanup_expired_access(self):
        """Очистка истекшего доступа"""
        try:
            expired_users = self.db.get_expired_users()
            revoked_count = self.db.revoke_expired_access()
            
            if revoked_count > 0:
                logger.info(f"Отозван доступ у {revoked_count} пользователей")
                
                # Удаляем пользователей из каналов и уведомляем
                for user_id in expired_users:
                    try:
                        # Удаляем из каналов
                        await self.channel_manager.revoke_access_from_user(user_id)
                        
                        # Уведомляем пользователя
                        from telegram import Bot
                        bot = Bot(token=BOT_TOKEN)
                        await bot.send_message(
                            chat_id=user_id,
                            text="⏰ Ваш доступ к материалам Аскезы истек. Для продления обратитесь к боту."
                        )
                    except Exception as e:
                        logger.error(f"Не удалось обработать пользователя {user_id}: {e}")
            
        except Exception as e:
            logger.error(f"Ошибка при очистке истекшего доступа: {e}")
    
    async def periodic_cleanup(self):
        """Периодическая очистка истекшего доступа"""
        while True:
            await asyncio.sleep(3600)  # Проверяем каждый час
            await self.cleanup_expired_access()
    
    def start_cleanup_task(self):
        """Запуск задачи периодической очистки"""
        import threading
        import time
        
        def cleanup_worker():
            while True:
                time.sleep(3600)  # Ждем час
                # Создаем новый event loop для очистки
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.cleanup_expired_access())
                loop.close()
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def run(self):
        """Запуск бота"""
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN не установлен!")
            return
        
        if not YOOKASSA_SECRET_KEY or YOOKASSA_SECRET_KEY.startswith('test_YOUR_'):
            logger.warning("YOOKASSA_SECRET_KEY не настроен! Платежи не будут работать.")
            logger.warning("Смотрите инструкции в файле YOOKASSA_SETUP.md")
        
        # Создаем приложение
        self.application = Application.builder().token(BOT_TOKEN).build()
        
        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.handle_message))
        self.application.add_handler(CallbackQueryHandler(self.handlers.button_callback))
        
        logger.info("Обработчики зарегистрированы:")
        logger.info("- CommandHandler для /start")
        logger.info("- MessageHandler для текстовых сообщений")
        logger.info("- CallbackQueryHandler для кнопок")
        
        # Обработчик для webhook от ЮKassa (если используется) - отключен для избежания конфликтов
        # self.application.add_handler(
        #     MessageHandler(filters.TEXT & ~filters.COMMAND, self.webhook_handler)
        # )
        
        # Обработчик ошибок
        self.application.add_error_handler(self.handlers.error_handler)
        
        # Запускаем задачу периодической очистки (отключено для отладки)
        # self.start_cleanup_task()
        
        logger.info("Бот запущен!")
        
        # Запускаем бота
        self.application.run_polling()

if __name__ == "__main__":
    bot = AskezaBot()
    bot.run()
