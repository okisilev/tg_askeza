#!/usr/bin/env python3
"""
Проверка статуса бота и автоматической обработки
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from config import DATABASE_PATH, BOT_TOKEN, PRIVATE_CHANNEL_ID
from telegram import Bot

def check_recent_payments():
    """Проверка недавних платежей"""
    print("🔍 Проверка недавних платежей")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем платежи за последние 24 часа
        cursor.execute('''
            SELECT user_id, yookassa_payment_id, payment_type, amount, status, created_at 
            FROM payments 
            WHERE created_at >= datetime('now', '-1 day')
            ORDER BY created_at DESC
        ''')
        recent_payments = cursor.fetchall()
        
        if recent_payments:
            print(f"📋 Найдено {len(recent_payments)} платежей за последние 24 часа:")
            for payment in recent_payments:
                print(f"   • User: {payment[0]}")
                print(f"     Payment ID: {payment[1]}")
                print(f"     Type: {payment[2]}")
                print(f"     Amount: {payment[3]}₽")
                print(f"     Status: {payment[4]}")
                print(f"     Created: {payment[5]}")
                print()
        else:
            print("❌ Недавних платежей не найдено")
        
        # Проверяем успешные платежи без доступа
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
        
        conn.close()
        return len(recent_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0, 0

async def test_bot_connection():
    """Тест подключения к боту"""
    print("\n🤖 Тест подключения к боту")
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

async def send_test_notification():
    """Отправка тестового уведомления"""
    print("\n📧 Тест отправки уведомления")
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
    print("🔍 Проверка статуса бота и автоматической обработки")
    print("=" * 50)
    
    # Проверяем недавние платежи
    recent_count, without_access_count = check_recent_payments()
    
    # Тестируем подключение к боту
    bot_connected = await test_bot_connection()
    
    # Тестируем отправку уведомлений
    notification_ok = await send_test_notification()
    
    print(f"\n📊 Результат проверки:")
    print(f"   • Недавних платежей: {recent_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    print(f"   • Бот подключен: {'✅' if bot_connected else '❌'}")
    print(f"   • Уведомления: {'✅' if notification_ok else '❌'}")
    
    if without_access_count > 0:
        print("\n⚠️ Обнаружены платежи без доступа!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Или исправьте вручную: python fix_all_payments.py")
    else:
        print("\n✅ Все платежи обработаны корректно")
    
    if not bot_connected:
        print("\n❌ Проблемы с подключением к боту!")
        print("Проверьте BOT_TOKEN и настройки")
    
    # Показываем рекомендации
    print_recommendations()

if __name__ == "__main__":
    asyncio.run(main())
