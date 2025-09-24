import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замените на ваш)
BOT_TOKEN = "8175601106:AAEYmyV6RZ_9vOJYzwGDDdcIt87B8yZYyR0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    
    keyboard = [
        [InlineKeyboardButton("❓ Вопрос/Ответ", callback_data="faq")],
        [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("Тестовый бот. Нажмите на кнопку:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Получен callback: {query.data} от пользователя {query.from_user.id}")
    
    if query.data == "faq":
        await query.edit_message_text("FAQ работает!")
    elif query.data == "payment":
        await query.edit_message_text("Оплата работает!")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    logger.info("Тестовый бот запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
