from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging

BOT_TOKEN = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def get_channel_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    chat_id = chat.id
    chat_title = chat.title or "Неизвестно"
    chat_type = chat.type

    response = f"""
📊 Информация о чате:
ID: `{chat_id}`
Название: {chat_title}
Тип: {chat_type}
    """
    await update.message.reply_text(response, parse_mode='Markdown')

async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    logger.info(f"📩 ПОЛУЧЕНО СООБЩЕНИЕ В ЧАТЕ: ID={chat.id}, Type={chat.type}, Title={chat.title}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Команда для ручного запроса
    application.add_handler(CommandHandler("get_channel_id", get_channel_id))

    # Логируем ВСЕ сообщения — ключ к решению!
    application.add_handler(MessageHandler(filters.ALL, log_all_messages))

    print("🤖 Бот запущен. Отправьте /get_channel_id в закрытом канале.")
    print("👀 Смотрите логи — там будет ID канала!")
    application.run_polling()

if __name__ == '__main__':
    main()