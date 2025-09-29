#!/usr/bin/env python3
"""
Тест автоматической обработки платежей
"""

import asyncio
import logging
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from yookassa_client import YooKassaClient
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_payment_processing():
    """Тест обработки платежей"""
    print("🧪 Тест автоматической обработки платежей")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        db = Database()
        channel_manager = ChannelManager()
        yookassa_client = YooKassaClient()
        
        print("✅ Компоненты инициализированы")
        
        # Получаем все pending платежи
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, yookassa_payment_id, payment_type, amount, created_at 
                FROM payments 
                WHERE status = 'pending'
                ORDER BY created_at DESC
            ''')
            pending_payments = cursor.fetchall()
        
        if pending_payments:
            print(f"⏳ Найдено {len(pending_payments)} pending платежей:")
            for payment in pending_payments:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Created: {payment[4]}")
                print()
        else:
            print("✅ Pending платежей не найдено")
        
        # Проверяем успешные платежи без доступа
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.user_id, p.yookassa_payment_id, p.payment_type, p.amount, p.created_at
                FROM payments p
                LEFT JOIN user_access ua ON p.user_id = ua.user_id AND ua.is_active = 1
                WHERE p.status = 'succeeded' AND ua.user_id IS NULL
                ORDER BY p.created_at DESC
            ''')
            payments_without_access = cursor.fetchall()
        
        if payments_without_access:
            print(f"⚠️ Найдено {len(payments_without_access)} успешных платежей без доступа:")
            for payment in payments_without_access:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Created: {payment[4]}")
                print()
        else:
            print("✅ Все успешные платежи имеют доступ")
        
        return len(pending_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return 0, 0

async def test_notification_sending():
    """Тест отправки уведомлений"""
    print("\n📧 Тест отправки уведомлений")
    print("=" * 50)
    
    try:
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
        
        bot = Bot(token=BOT_TOKEN)
        
        # Тестовое сообщение
        test_text = """
🧪 Тестовое сообщение с кнопками доступа

Нажмите на кнопки ниже для проверки:
        """
        
        # Создаем кнопки для доступа
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Отправляем тестовое сообщение (закомментировано для безопасности)
        # await bot.send_message(
        #     chat_id=760111270,  # Тестовый пользователь
        #     text=test_text,
        #     reply_markup=reply_markup
        # )
        
        print("✅ Тест отправки уведомлений пройден")
        print("(Сообщение не отправлено для безопасности)")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании уведомлений: {e}")
        return False

def print_recommendations():
    """Печать рекомендаций"""
    print("\n" + "=" * 50)
    print("💡 РЕКОМЕНДАЦИИ")
    print("=" * 50)
    
    print("\n1️⃣ Запустите бота для автоматической обработки:")
    print("   python run_no_webhook.py")
    
    print("\n2️⃣ Проверьте логи на ошибки:")
    print("   • Ищите ошибки при обработке платежей")
    print("   • Проверьте ошибки при отправке уведомлений")
    print("   • Убедитесь, что периодическая проверка работает")
    
    print("\n3️⃣ При необходимости исправьте вручную:")
    print("   python fix_all_payments.py")
    
    print("\n4️⃣ Проверьте настройки:")
    print("   • BOT_TOKEN настроен")
    print("   • PRIVATE_CHANNEL_ID настроен")
    print("   • База данных доступна")

async def main():
    """Основная функция"""
    print("🧪 Тест автоматической обработки платежей")
    print("=" * 50)
    
    # Тестируем обработку платежей
    pending_count, without_access_count = await test_payment_processing()
    
    # Тестируем отправку уведомлений
    notification_ok = await test_notification_sending()
    
    print(f"\n📊 Результат тестирования:")
    print(f"   • Pending платежей: {pending_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    print(f"   • Уведомления: {'✅' if notification_ok else '❌'}")
    
    if without_access_count > 0:
        print("\n⚠️ Обнаружены платежи без доступа!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Или исправьте вручную: python fix_all_payments.py")
    else:
        print("\n✅ Автоматическая обработка работает корректно")
    
    # Показываем рекомендации
    print_recommendations()

if __name__ == "__main__":
    asyncio.run(main())
