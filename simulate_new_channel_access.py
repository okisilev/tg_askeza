#!/usr/bin/env python3
"""
Скрипт для симуляции добавления пользователя в новый канал
ID=-2073129707770, Type=supergroup, Title=Аскеза✨ Верь в себя!
"""

import asyncio
import logging
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def simulate_successful_payment_new_channel(user_id: int, payment_type: str = "askeza"):
    """Симуляция успешного платежа с доступом к новому каналу"""
    print(f"🎭 Симуляция успешного платежа с доступом к каналу 'Аскеза✨ Верь в себя!'")
    print(f"Пользователь: {user_id}")
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
        
        # 3. Добавляем пользователя в новый канал
        print("📺 Добавляем пользователя в канал 'Аскеза✨ Верь в себя!'...")
        try:
            success = await channel_manager.grant_access_to_user(user_id, payment_type)
            if success:
                print("✅ Пользователь добавлен в канал")
            else:
                print("⚠️ Не удалось добавить пользователя в канал")
        except Exception as e:
            print(f"⚠️ Ошибка при добавлении в канал: {e}")
        
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
        
        # Создаем кнопки для доступа
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
        try:
            in_channel = await channel_manager.check_user_in_channel(user_id)
            print(f"📺 В канале 'Аскеза✨ Верь в себя!': {in_channel}")
        except Exception as e:
            print(f"⚠️ Ошибка проверки канала: {e}")
        
        # Проверяем подписку на чат
        try:
            in_chat = await channel_manager.check_user_in_chat(user_id)
            print(f"💬 В чате: {in_chat}")
        except Exception as e:
            print(f"⚠️ Ошибка проверки чата: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при симуляции платежа: {e}")
        return False

def print_instructions():
    """Печать инструкций"""
    print("\n" + "=" * 50)
    print("📋 ИНСТРУКЦИИ ПО ПРОВЕРКЕ НОВОГО КАНАЛА")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте, что пользователь получил:")
    print("   • Сообщение об успешной оплате")
    print("   • Кнопки '📺 Закрытый канал' и '💬 Закрытый чат'")
    print("   • Кнопку '🏠 Главное меню'")
    
    print("\n2️⃣ Проверьте работу кнопок:")
    print("   • Нажмите '📺 Закрытый канал'")
    print("   • Нажмите '💬 Закрытый чат'")
    print("   • Нажмите '🏠 Главное меню'")
    
    print("\n3️⃣ Проверьте логи бота:")
    print("   • Ищите ошибки при отправке сообщений")
    print("   • Проверьте обработку callback'ов")
    print("   • Убедитесь, что кнопки работают")
    
    print("\n4️⃣ Проверьте доступ к каналу 'Аскеза✨ Верь в себя!':")
    print("   • Убедитесь, что пользователь добавлен в канал")
    print("   • Проверьте, что бот имеет права администратора")
    print("   • Убедитесь, что канал существует")
    
    print("\n5️⃣ Если кнопки не работают:")
    print("   • Проверьте, что бот запущен")
    print("   • Убедитесь, что handlers.py обрабатывает callback'и")
    print("   • Проверьте права бота в канале")

async def main():
    """Основная функция"""
    user_id = 431292182  # Тестовый пользователь из логов
    
    print("🎭 Симуляция успешного платежа с доступом к каналу 'Аскеза✨ Верь в себя!'")
    print("ID=-2073129707770, Type=supergroup")
    print("=" * 50)
    
    # Симулируем успешный платеж
    success = await simulate_successful_payment_new_channel(user_id)
    
    if success:
        print("\n✅ Симуляция успешного платежа завершена")
        print("Проверьте, получил ли пользователь уведомление с кнопками")
    else:
        print("\n❌ Симуляция не удалась")
        print("Проверьте ошибки выше")
    
    # Показываем инструкции
    print_instructions()
    
    print("\n🚀 Для запуска бота используйте:")
    print("   python run_simple_bot.py")
    print("   или")
    print("   python run_no_webhook.py")

if __name__ == "__main__":
    asyncio.run(main())
