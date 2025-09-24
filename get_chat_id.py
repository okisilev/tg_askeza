from aiogram import Bot, Dispatcher, types
import asyncio

BOT_TOKEN = "8175601106:AAEYmyV6RZ_9vOJYzwGDDdcIt87B8yZYyR0"

# ЗАМЕНИТЕ НА СВОЙ ID (число), чтобы бот прислал ID канала в личку
YOUR_USER_ID = 431292182  # Пример: 123456789

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: types.Message):
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