from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging

BOT_TOKEN = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def log_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    logger.info(f"📩 ПОЛУЧЕНО СООБЩЕНИЕ В ЧАТЕ: ID={chat.id}, Type={chat.type}, Title={chat.title}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.ALL, log_all_messages))
    print("🤖 Бот запущен. Отправьте 'Тест' в канал — и посмотрите логи!")
    application.run_polling()

if __name__ == '__main__':
    main()