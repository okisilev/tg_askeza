#!/usr/bin/env python3
"""
Скрипт для симуляции успешного платежа и проверки уведомлений
"""

import asyncio
import logging
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def simulate_successful_payment(user_id: int, payment_type: str = "askeza"):
    """Симуляция успешного платежа"""
    print(f"🎭 Симуляция успешного платежа для пользователя {user_id}")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        db = Database()
        channel_manager = ChannelManager()
        bot = Bot(token=BOT_TOKEN)
        
        print("✅ Компоненты инициализированы")
        
        # 1. Создаем тестовый платеж
        payment_id = f"test_payment_{user_id}_{int(datetime.now().timestamp())}"
        print(f"📝 Создаем тестовый платеж: {payment_id}")
        
        # Добавляем платеж в базу данных
        db.create_payment(user_id, payment_id, payment_type, 990, "succeeded")
        print("✅ Платеж создан в базе данных")
        
        # 2. Предоставляем доступ
        print("🔐 Предоставляем доступ...")
        if db.grant_access(user_id, payment_type):
            print("✅ Доступ предоставлен")
        else:
            print("❌ Не удалось предоставить доступ")
            return False
        
        # 3. Добавляем пользователя в каналы
        print("📺 Добавляем пользователя в каналы...")
        success = await channel_manager.grant_access_to_user(user_id, payment_type)
        if success:
            print("✅ Пользователь добавлен в каналы")
        else:
            print("⚠️ Не удалось добавить пользователя в каналы")
        
        # 4. Отправляем уведомление с кнопками
        print("📧 Отправляем уведомление с кнопками...")
        
        success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к {payment_type}.

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
        
        print("✅ Уведомление с кнопками отправлено")
        
        # 5. Проверяем результат
        print("\n🔍 Проверяем результат:")
        
        # Проверяем доступ в базе данных
        user_access = db.get_user_access(user_id)
        if user_access:
            print(f"✅ Доступ в БД: {user_access[2]} (активен: {user_access[5]})")
        else:
            print("❌ Доступ в БД не найден")
        
        # Проверяем подписку на канал
        in_channel = await channel_manager.check_user_in_channel(user_id)
        print(f"📺 В канале: {in_channel}")
        
        # Проверяем подписку на чат
        in_chat = await channel_manager.check_user_in_chat(user_id)
        print(f"💬 В чате: {in_chat}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при симуляции платежа: {e}")
        return False

async def test_callback_handling(user_id: int):
    """Тест обработки callback'ов"""
    print(f"\n🔘 Тестирование обработки callback'ов для пользователя {user_id}")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Отправляем тестовое сообщение с кнопками
        test_text = """
🧪 Тестовое сообщение с кнопками

Нажмите на кнопки ниже для проверки:
        """
        
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await bot.send_message(
            chat_id=user_id,
            text=test_text,
            reply_markup=reply_markup
        )
        
        print("✅ Тестовое сообщение с кнопками отправлено")
        print("Проверьте, работают ли кнопки в боте")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании callback'ов: {e}")
        return False

def print_troubleshooting():
    """Печать инструкций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 УСТРАНЕНИЕ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте логи бота:")
    print("   • Ищите ошибки при отправке сообщений")
    print("   • Проверьте обработку webhook'ов")
    print("   • Убедитесь, что callback'и обрабатываются")
    
    print("\n2️⃣ Проверьте настройки:")
    print(f"   • BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
    print(f"   • PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
    print(f"   • PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
    
    print("\n3️⃣ Проверьте права бота:")
    print("   • Бот должен быть администратором канала")
    print("   • У бота должны быть права на приглашение пользователей")
    print("   • Пользователь не должен блокировать бота")
    
    print("\n4️⃣ Проверьте базу данных:")
    print("   • Пользователь должен быть в таблице users")
    print("   • Должен быть активный доступ в user_access")
    print("   • Должен быть успешный платеж в payments")
    
    print("\n5️⃣ Проверьте webhook:")
    print("   • Webhook должен быть настроен в ЮKassa")
    print("   • URL должен быть доступен")
    print("   • Обработка webhook'ов должна работать")

async def main():
    """Основная функция"""
    user_id = 777785057  # Тестовый пользователь
    
    print("🎭 Симуляция успешного платежа")
    print("=" * 50)
    
    # Симулируем успешный платеж
    success = await simulate_successful_payment(user_id)
    
    if success:
        print("\n✅ Симуляция успешного платежа завершена")
        print("Проверьте, получил ли пользователь уведомление с кнопками")
    else:
        print("\n❌ Симуляция не удалась")
    
    # Тестируем callback'и
    await test_callback_handling(user_id)
    
    # Показываем инструкции по устранению неполадок
    print_troubleshooting()

if __name__ == "__main__":
    asyncio.run(main())
