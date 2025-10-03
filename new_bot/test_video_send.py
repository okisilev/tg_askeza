#!/usr/bin/env python3
"""
Тест отправки видео
"""

import asyncio
import logging
from telegram import Bot
from config import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_video_send():
    """Тестирует отправку видео"""
    
    print("🎥 Тестирование отправки видео...")
    
    try:
        # Создаем бота
        bot = Bot(token=config.BOT_TOKEN)
        await bot.initialize()
        print("✅ Бот инициализирован")
        
        # Тестовый пользователь
        test_user_id = 431292182
        
        # Проверяем существование файла
        try:
            with open("start.mp4", "rb") as video_file:
                print("✅ Файл start.mp4 найден и открыт")
                
                # Отправляем видео
                await bot.send_video(
                    chat_id=test_user_id,
                    video=video_file,
                    caption="Добро пожаловать! 🌸"
                )
                
                print("✅ Видео отправлено успешно")
                
        except FileNotFoundError:
            print("❌ Файл start.mp4 не найден")
        except Exception as e:
            print(f"❌ Ошибка при отправке видео: {e}")
        
        print("✅ Тест завершен")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        logger.error(f"Общая ошибка: {e}")
    finally:
        try:
            await bot.shutdown()
            print("✅ Бот закрыт")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_video_send())
