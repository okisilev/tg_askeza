from aiogram import Bot, Dispatcher, types
import asyncio

import logging
logging.basicConfig(level=logging.INFO)
# ЗАМЕНИТЕ НА СВОЙ ТОКЕН
BOT_TOKEN = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"

# ЗАМЕНИТЕ НА СВОЙ ID (число), чтобы бот прислал ID канала в личку
YOUR_USER_ID = 431292182  # Пример: 123456789

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
    logging.info(f"Получено сообщение из чата: {message.chat.id}")
    # Получаем ID чата, откуда пришло сообщение (это ID канала)
    chat_id = message.chat.id

    # Опционально: получаем название канала
    chat_title = message.chat.title or "Приватный канал"

    # Отправляем ID канала в личку пользователю
    await bot.send_message(
        chat_id=YOUR_USER_ID,
        text=f"ID канала: `{chat_id}`\nНазвание: {chat_title}",
        parse_mode="Markdown"
    )

    # (Опционально) Ответить в канал
    await message.answer(f"ID этого канала: `{chat_id}`", parse_mode="Markdown")

async def main():
    print("Бот запущен. Добавьте его в канал, отправьте сообщение и получите ID.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())