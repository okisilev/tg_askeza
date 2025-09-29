#!/usr/bin/env python3
"""
Отправка уведомления пользователю 760111270 прямо сейчас
"""

import asyncio
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_notification_now():
    """Отправка уведомления прямо сейчас"""
    print("📧 Отправка уведомления пользователю 760111270")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Инициализируем бота
        await bot.initialize()
        print("✅ Бот инициализирован")
        
        # Проверяем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот: @{bot_info.username} ({bot_info.first_name})")
        
        # Создаем сообщение с кнопками
        success_text = """
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к Аскезе.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
        """
        
        # Создаем кнопки для доступа
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем сообщение
        message = await bot.send_message(
            chat_id=760111270,
            text=success_text,
            reply_markup=reply_markup
        )
        
        print(f"✅ Сообщение отправлено: {message.message_id}")
        print("✅ Пользователь должен получить кнопки доступа!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке сообщения: {e}")
        return False

async def test_bot_connection():
    """Тест подключения к боту"""
    print("🤖 Тест подключения к боту")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"   • ID: {bot_info.id}")
        print(f"   • Имя: {bot_info.first_name}")
        print(f"   • Username: @{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False

async def main():
    """Основная функция"""
    print("🚀 Отправка уведомления пользователю 760111270")
    print("=" * 50)
    
    # Тестируем подключение
    connection_ok = await test_bot_connection()
    
    if not connection_ok:
        print("❌ Не удалось подключиться к боту")
        return
    
    # Отправляем уведомление
    notification_sent = await send_notification_now()
    
    if notification_sent:
        print("\n🎉 Уведомление отправлено!")
        print("Пользователь 760111270 должен получить кнопки доступа")
    else:
        print("\n❌ Не удалось отправить уведомление")
        print("Проверьте настройки бота и права доступа")

if __name__ == "__main__":
    asyncio.run(main())
