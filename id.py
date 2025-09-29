import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(
        "🔧 **100% рабочий способ получить ID приватного канала:**\n\n"
        "1. 📢 Создайте временный ПУБЛИЧНЫЙ канал\n"
        "2. 👥 Добавьте этого бота в него как администратора\n"
        "3. 🔄 Перешлите сообщение из приватного канала в публичный\n"
        "4. 📋 Бот автоматически покажет ID приватного канала\n\n"
        "Или используйте метод ниже ⬇️"
    )

async def alternative_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Альтернативный метод через API"""
    await update.message.reply_text(
        "🔐 **Метод для разработчиков (гарантированно работает):**\n\n"
        "1. Откройте https://my.telegram.org/apps\n"
        "2. Авторизуйтесь и получите API_ID и API_HASH\n"
        "3. Используйте этот код для получения ID:\n\n"
        "```python\n"
        "from telethon import TelegramClient\n\n"
        "api_id = 'YOUR_API_ID'\n"
        "api_hash = 'YOUR_API_HASH'\n\n"
        "async def main():\n"
        "    async with TelegramClient('session', api_id, api_hash) as client:\n"
        "        dialogs = await client.get_dialogs()\n"
        "        for dialog in dialogs:\n"
        "            if dialog.is_channel:\n"
        "                print(f'Channel: {dialog.name}, ID: {dialog.id}')\n\n"
        "import asyncio\n"
        "asyncio.run(main())\n"
        "```",
        parse_mode='Markdown'
    )

async def create_helper_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Инструкция по созданию канала-помощника"""
    await update.message.reply_text(
        "📋 **Пошаговая инструкция:**\n\n"
        "1. 📱 В Telegram нажмите → Создать канал\n"
        "2. 📢 Название: 'Временный канал для ID'\n"
        "3. 🔓 Тип: ПУБЛИЧНЫЙ (важно!)\n"
        "4. 🌐 Username: любой свободный\n"
        "5. 👥 Добавьте @raw_data_bot в канал\n"
        "6. 🔄 Перешлите сообщение из приватного канала\n"
        "7. 📊 Бот покажет все данные включая chat_id\n\n"
        "После получения ID можете удалить временный канал",
        parse_mode='Markdown'
    )

async def handle_forwarded_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик пересланных сообщений"""
    try:
        if update.message.forward_from_chat:
            chat = update.message.forward_from_chat
            await update.message.reply_text(
                f"✅ Данные получены!\n"
                f"🆔 ID: `{chat.id}`\n"
                f"📛 Название: {chat.title}\n"
                f"👤 Тип: {chat.type}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "❌ Сообщение не содержит данных о канале.\n"
                "Убедитесь, что пересылка разрешена в настройках канала."
            )
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("api_method", alternative_method))
    application.add_handler(CommandHandler("helper", create_helper_channel))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_forwarded_message))

    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()