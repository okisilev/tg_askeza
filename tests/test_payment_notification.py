#!/usr/bin/env python3
"""
Тестовый скрипт для проверки уведомлений после успешной оплаты
"""

import asyncio
import logging
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_payment_notification(user_id: int):
    """Тест отправки уведомления после успешной оплаты"""
    print(f"🧪 Тестирование уведомления для пользователя {user_id}")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        bot = Bot(token=BOT_TOKEN)
        db = Database()
        channel_manager = ChannelManager()
        
        print("✅ Компоненты инициализированы")
        
        # Проверяем пользователя в базе данных
        user = db.get_user(user_id)
        if not user:
            print(f"❌ Пользователь {user_id} не найден в базе данных")
            return False
        
        print(f"✅ Пользователь найден: {user[1]}")
        
        # Проверяем доступ пользователя
        user_access = db.get_user_access(user_id)
        if not user_access:
            print(f"❌ У пользователя {user_id} нет активного доступа")
            return False
        
        print(f"✅ У пользователя есть активный доступ: {user_access[2]}")
        
        # Проверяем подписку на канал
        in_channel = await channel_manager.check_user_in_channel(user_id)
        print(f"📺 Пользователь в канале: {in_channel}")
        
        # Проверяем подписку на чат
        in_chat = await channel_manager.check_user_in_chat(user_id)
        print(f"💬 Пользователь в чате: {in_chat}")
        
        # Отправляем тестовое уведомление
        print("\n📧 Отправляем тестовое уведомление...")
        
        success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к Аскезе.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
        """
        
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=user_id,
            text=success_text,
            reply_markup=reply_markup
        )
        
        print("✅ Тестовое уведомление отправлено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")
        return False

async def test_channel_access(user_id: int):
    """Тест доступа к каналу"""
    print(f"\n📺 Тестирование доступа к каналу для пользователя {user_id}")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        channel_manager = ChannelManager()
        
        # Проверяем подписку на канал
        in_channel = await channel_manager.check_user_in_channel(user_id)
        print(f"Пользователь в канале: {in_channel}")
        
        if not in_channel:
            print("Пытаемся добавить пользователя в канал...")
            success = await channel_manager.add_user_to_channel(user_id)
            print(f"Результат добавления: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании доступа к каналу: {e}")
        return False

def print_debug_info():
    """Печать отладочной информации"""
    print("\n" + "=" * 50)
    print("🔍 ОТЛАДОЧНАЯ ИНФОРМАЦИЯ")
    print("=" * 50)
    
    print(f"BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
    print(f"PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
    print(f"PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
    
    print("\n📋 Возможные причины проблемы:")
    print("1. Пользователь не получает уведомление после оплаты")
    print("2. Callback'и не обрабатываются правильно")
    print("3. Бот не может отправить сообщение пользователю")
    print("4. Пользователь заблокировал бота")
    print("5. Webhook не обрабатывает платежи правильно")

async def main():
    """Основная функция"""
    user_id = 777785057  # Тестовый пользователь
    
    print("🧪 Тестирование уведомлений после оплаты")
    print("=" * 50)
    
    # Тестируем уведомление
    success = await test_payment_notification(user_id)
    
    if success:
        print("\n✅ Тест уведомления пройден")
    else:
        print("\n❌ Тест уведомления не пройден")
    
    # Тестируем доступ к каналу
    await test_channel_access(user_id)
    
    # Показываем отладочную информацию
    print_debug_info()
    
    print("\n📋 Рекомендации:")
    print("1. Проверьте логи бота на наличие ошибок")
    print("2. Убедитесь, что webhook обрабатывает платежи")
    print("3. Проверьте, что пользователь не заблокировал бота")
    print("4. Убедитесь, что callback'и обрабатываются правильно")

if __name__ == "__main__":
    asyncio.run(main())
