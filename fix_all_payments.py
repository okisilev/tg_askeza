#!/usr/bin/env python3
"""
Исправление всех платежей без доступа
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN

def get_payments_without_access():
    """Получение платежей без доступа"""
    print("🔍 Поиск платежей без доступа")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
        cursor = conn.cursor()
        
        # Находим успешные платежи без доступа
        cursor.execute('''
            SELECT p.user_id, p.yookassa_payment_id, p.payment_type, p.amount, p.created_at
            FROM payments p
            LEFT JOIN user_access ua ON p.user_id = ua.user_id AND ua.is_active = 1
            WHERE p.status = 'succeeded' AND ua.user_id IS NULL
            ORDER BY p.created_at DESC
        ''')
        payments_without_access = cursor.fetchall()
        
        print(f"📋 Найдено {len(payments_without_access)} платежей без доступа:")
        for payment in payments_without_access:
            print(f"   • User: {payment[0]}")
            print(f"     Payment ID: {payment[1]}")
            print(f"     Type: {payment[2]}")
            print(f"     Amount: {payment[3]}₽")
            print(f"     Created: {payment[4]}")
            print()
        
        conn.close()
        return payments_without_access
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return []

def grant_access_to_user(user_id: int, payment_type: str):
    """Предоставление доступа пользователю"""
    print(f"🔐 Предоставление доступа пользователю {user_id}")
    
    try:
        conn = sqlite3.connect('askeza_bot.db')
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
            conn.close()
            return True
        
        # Создаем новый доступ
        expires_at = datetime.now() + timedelta(days=30)
        cursor.execute('''
            INSERT INTO user_access (user_id, access_type, expires_at, is_active)
            VALUES (?, ?, ?, ?)
        ''', (user_id, payment_type, expires_at, 1))
        
        print(f"✅ Доступ предоставлен до {expires_at}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при предоставлении доступа: {e}")
        return False

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
        
        print(f"✅ Уведомление отправлено пользователю {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False

async def process_payment(user_id: int, payment_id: str, payment_type: str, amount: float):
    """Обработка платежа"""
    print(f"\n💳 Обработка платежа {payment_id} для пользователя {user_id}")
    print("=" * 50)
    
    # Предоставляем доступ
    access_granted = grant_access_to_user(user_id, payment_type)
    
    if not access_granted:
        print(f"❌ Не удалось предоставить доступ пользователю {user_id}")
        return False
    
    # Отправляем уведомление
    notification_sent = await send_notification_to_user(user_id)
    
    if not notification_sent:
        print(f"❌ Не удалось отправить уведомление пользователю {user_id}")
        return False
    
    print(f"✅ Платеж {payment_id} обработан успешно")
    return True

async def main():
    """Основная функция"""
    print("🔧 Исправление всех платежей без доступа")
    print("=" * 50)
    
    # Получаем платежи без доступа
    payments_without_access = get_payments_without_access()
    
    if not payments_without_access:
        print("✅ Все платежи имеют доступ")
        return
    
    print(f"🔄 Обрабатываем {len(payments_without_access)} платежей...")
    
    success_count = 0
    for payment in payments_without_access:
        user_id, payment_id, payment_type, amount, created_at = payment
        
        try:
            success = await process_payment(user_id, payment_id, payment_type, amount)
            if success:
                success_count += 1
        except Exception as e:
            print(f"❌ Ошибка при обработке платежа {payment_id}: {e}")
    
    print(f"\n📊 Результат:")
    print(f"   • Обработано: {success_count}/{len(payments_without_access)}")
    print(f"   • Успешно: {success_count}")
    print(f"   • Ошибок: {len(payments_without_access) - success_count}")
    
    if success_count == len(payments_without_access):
        print("\n🎉 Все платежи обработаны успешно!")
        print("Пользователи должны получить кнопки доступа")
    else:
        print("\n⚠️ Некоторые платежи не удалось обработать")
        print("Проверьте логи на ошибки")

if __name__ == "__main__":
    asyncio.run(main())
