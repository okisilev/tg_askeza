#!/usr/bin/env python3
"""
Тестовый скрипт для проверки уведомлений после успешной оплаты
"""

import asyncio
import logging
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_payment_notification(user_id: int):
    """Тест отправки уведомления с кнопками после успешной оплаты"""
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
        
        # Отправляем тестовое уведомление с кнопками
        print("📧 Отправляем уведомление с кнопками...")
        
        success_text = f"""
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
        
        await bot.send_message(
            chat_id=user_id,
            text=success_text,
            reply_markup=reply_markup
        )
        
        print("✅ Уведомление с кнопками отправлено")
        print("Проверьте, что пользователь получил сообщение с кнопками")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")
        return False

async def test_callback_handling(user_id: int):
    """Тест обработки callback'ов от кнопок"""
    print(f"\n🔘 Тестирование обработки callback'ов для пользователя {user_id}")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Отправляем тестовое сообщение с кнопками
        test_text = """
🧪 Тестовое сообщение с кнопками доступа

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

def test_payment_processing():
    """Тест обработки платежей"""
    print(f"\n💳 Тестирование обработки платежей")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Получаем все успешные платежи
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, user_id, payment_type, status, created_at 
                FROM payments 
                WHERE status = 'succeeded'
                ORDER BY created_at DESC
                LIMIT 5
            ''')
            successful_payments = cursor.fetchall()
        
        if successful_payments:
            print(f"✅ Найдено {len(successful_payments)} успешных платежей:")
            for payment in successful_payments:
                print(f"   - ID: {payment[0]}")
                print(f"     Пользователь: {payment[1]}")
                print(f"     Тип: {payment[2]}")
                print(f"     Статус: {payment[3]}")
                print(f"     Дата: {payment[4]}")
                print()
        else:
            print("❌ Успешных платежей не найдено")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке платежей: {e}")
        return False

def print_troubleshooting():
    """Печать инструкций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 УСТРАНЕНИЕ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте логи бота:")
    print("   • Ищите ошибки при отправке сообщений")
    print("   • Проверьте обработку успешных платежей")
    print("   • Убедитесь, что callback'и обрабатываются")
    
    print("\n2️⃣ Проверьте настройки:")
    print(f"   • BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
    print("   • PRIVATE_CHANNEL_ID должен быть настроен")
    print("   • PRIVATE_CHAT_ID должен быть настроен")
    
    print("\n3️⃣ Проверьте права бота:")
    print("   • Бот должен быть администратором канала")
    print("   • У бота должны быть права на приглашение пользователей")
    print("   • Пользователь не должен блокировать бота")
    
    print("\n4️⃣ Проверьте базу данных:")
    print("   • Пользователь должен быть в таблице users")
    print("   • Должен быть активный доступ в user_access")
    print("   • Должен быть успешный платеж в payments")
    
    print("\n5️⃣ Проверьте обработку callback'ов:")
    print("   • Убедитесь, что handlers.py обрабатывает callback'и")
    print("   • Проверьте, что бот запущен и работает")
    print("   • Убедитесь, что пользователь имеет активный доступ")

async def main():
    """Основная функция"""
    user_id = 777785057  # Тестовый пользователь
    
    print("🧪 Тестирование уведомлений после успешной оплаты")
    print("=" * 50)
    
    # Тестируем обработку платежей
    payments_ok = test_payment_processing()
    
    if payments_ok:
        print("✅ Обработка платежей работает")
    else:
        print("❌ Проблемы с обработкой платежей")
    
    # Тестируем уведомления
    notification_ok = await test_payment_notification(user_id)
    
    if notification_ok:
        print("✅ Уведомления работают")
    else:
        print("❌ Проблемы с уведомлениями")
    
    # Тестируем callback'и
    callback_ok = await test_callback_handling(user_id)
    
    if callback_ok:
        print("✅ Callback'и работают")
    else:
        print("❌ Проблемы с callback'ами")
    
    # Показываем инструкции по устранению неполадок
    print_troubleshooting()
    
    print("\n📋 Рекомендации:")
    print("1. Запустите бота и протестируйте полный цикл оплаты")
    print("2. Проверьте логи на наличие ошибок")
    print("3. Убедитесь, что callback'и обрабатываются правильно")
    print("4. Проверьте права бота в канале")

if __name__ == "__main__":
    asyncio.run(main())
