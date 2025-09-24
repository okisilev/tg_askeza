import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

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
        [KeyboardButton("❓ Вопрос/Ответ"), KeyboardButton("💳 Оплатить доступ")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("Тестовый бот с обычными кнопками. Нажмите на кнопку:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    user_id = update.effective_user.id
    
    logger.info(f"Получено сообщение: '{text}' от пользователя {user_id}")
    
    if text == "❓ Вопрос/Ответ":
        await update.message.reply_text("FAQ работает!")
    elif text == "💳 Оплатить доступ":
        await update.message.reply_text("Оплата работает!")
    else:
        await update.message.reply_text(f"Вы написали: {text}")

def main():
    """Запуск бота"""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Тестовый бот с обычными кнопками запущен!")
    application.run_polling()

if __name__ == "__main__":
    main()
