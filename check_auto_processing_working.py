#!/usr/bin/env python3
"""
Проверка работы автоматической обработки
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from config import DATABASE_PATH, BOT_TOKEN
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

def check_pending_payments():
    """Проверка pending платежей"""
    print("🔍 Проверка pending платежей")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем pending платежи
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
        return len(pending_payments), len(payments_without_access)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0, 0

async def send_notification_to_user(user_id: int):
    """Отправка уведомления пользователю"""
    print(f"📧 Отправка уведомления пользователю {user_id}")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
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
        
        print(f"✅ Уведомление с кнопками отправлено пользователю {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False

async def process_payment_manually(user_id: int, payment_id: str, payment_type: str, amount: float):
    """Ручная обработка платежа"""
    print(f"💳 Ручная обработка платежа {payment_id} для пользователя {user_id}")
    
    try:
        # Предоставляем доступ
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем, есть ли уже активный доступ
        cursor.execute('''
            SELECT id, access_type, is_active 
            FROM user_access 
            WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        existing_access = cursor.fetchone()
        
        if existing_access:
            print(f"✅ Активный доступ уже существует: {existing_access[1]}")
        else:
            # Создаем новый доступ
            expires_at = datetime.now() + timedelta(days=30)
            cursor.execute('''
                INSERT INTO user_access (user_id, access_type, expires_at, is_active)
                VALUES (?, ?, ?, ?)
            ''', (user_id, payment_type, expires_at, 1))
            
            print(f"✅ Доступ предоставлен до {expires_at}")
        
        conn.commit()
        conn.close()
        
        # Отправляем уведомление
        notification_sent = await send_notification_to_user(user_id)
        
        if notification_sent:
            print(f"✅ Платеж {payment_id} обработан успешно")
            return True
        else:
            print(f"❌ Не удалось отправить уведомление для платежа {payment_id}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при обработке платежа: {e}")
        return False

async def main():
    """Основная функция"""
    print("🔍 Проверка работы автоматической обработки")
    print("=" * 50)
    
    # Проверяем pending платежи
    pending_count, without_access_count = check_pending_payments()
    
    if without_access_count > 0:
        print(f"\n⚠️ Обнаружены {without_access_count} платежей без доступа!")
        print("Обрабатываем вручную...")
        
        # Получаем платежи без доступа
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.user_id, p.yookassa_payment_id, p.payment_type, p.amount, p.created_at
            FROM payments p
            LEFT JOIN user_access ua ON p.user_id = ua.user_id AND ua.is_active = 1
            WHERE p.status = 'succeeded' AND ua.user_id IS NULL
            ORDER BY p.created_at DESC
        ''')
        payments_without_access = cursor.fetchall()
        conn.close()
        
        # Обрабатываем каждый платеж
        success_count = 0
        for payment in payments_without_access:
            user_id, payment_id, payment_type, amount, created_at = payment
            
            try:
                success = await process_payment_manually(user_id, payment_id, payment_type, amount)
                if success:
                    success_count += 1
            except Exception as e:
                print(f"❌ Ошибка при обработке платежа {payment_id}: {e}")
        
        print(f"\n📊 Результат обработки:")
        print(f"   • Обработано: {success_count}/{len(payments_without_access)}")
        print(f"   • Успешно: {success_count}")
        print(f"   • Ошибок: {len(payments_without_access) - success_count}")
        
        if success_count == len(payments_without_access):
            print("\n🎉 Все платежи обработаны успешно!")
            print("Пользователи должны получить кнопки доступа")
        else:
            print("\n⚠️ Некоторые платежи не удалось обработать")
            print("Проверьте логи на ошибки")
    else:
        print("\n✅ Все платежи обработаны корректно")
    
    print("\n💡 Рекомендации:")
    print("1. Запустите бота: python run_no_webhook.py")
    print("2. Проверьте логи на ошибки")
    print("3. Убедитесь, что периодическая проверка работает")

if __name__ == "__main__":
    asyncio.run(main())
