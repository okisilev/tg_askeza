import asyncio
from aiogram import Bot

BOT_TOKEN = "8175601106:AAEYmyV6RZ_9vOJYzwGDDdcIt87B8yZYyR0"
# Создаём бота
bot = Bot(token=BOT_TOKEN)

async def get_channel_id():
    try:
        # Попробуем получить чат по username (если канал публичный)
        chat = await bot.get_chat("@test_askeza")
        print(f"ID канала: {chat.id}")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        await bot.session.close()  # Закрываем сессию

# Запускаем асинхронную функцию
if __name__ == "__main__":
    asyncio.run(get_channel_id())