#!/usr/bin/env python3
"""
Проверка уведомлений для конкретного пользователя
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from config import DATABASE_PATH, BOT_TOKEN
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

def check_user_payments(user_id: int):
    """Проверка платежей пользователя"""
    print(f"🔍 Проверка платежей пользователя {user_id}")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Проверяем все платежи пользователя
        cursor.execute('''
            SELECT yookassa_payment_id, payment_type, amount, status, created_at, paid_at
            FROM payments 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        user_payments = cursor.fetchall()
        
        if user_payments:
            print(f"📋 Найдено {len(user_payments)} платежей:")
            for payment in user_payments:
                print(f"   • Payment ID: {payment[0]}")
                print(f"     Type: {payment[1]}")
                print(f"     Amount: {payment[2]}₽")
                print(f"     Status: {payment[3]}")
                print(f"     Created: {payment[4]}")
                print(f"     Paid: {payment[5] or 'Не оплачен'}")
                print()
        else:
            print("❌ Платежей не найдено")
        
        # Проверяем доступ пользователя
        cursor.execute('''
            SELECT access_type, expires_at, is_active, created_at
            FROM user_access 
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        user_access = cursor.fetchall()
        
        if user_access:
            print(f"🔐 Найдено {len(user_access)} записей доступа:")
            for access in user_access:
                print(f"   • Type: {access[0]}")
                print(f"     Expires: {access[1]}")
                print(f"     Active: {access[2]}")
                print(f"     Created: {access[3]}")
                print()
        else:
            print("❌ Доступа не найдено")
        
        conn.close()
        return len(user_payments), len(user_access)
        
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

async def grant_access_to_user(user_id: int, payment_type: str):
    """Предоставление доступа пользователю"""
    print(f"🔐 Предоставление доступа пользователю {user_id}")
    
    try:
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
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при предоставлении доступа: {e}")
        return False

async def main():
    """Основная функция"""
    # Тестируем с пользователем 760111270
    user_id = 760111270
    
    print(f"🔍 Проверка уведомлений для пользователя {user_id}")
    print("=" * 50)
    
    # Проверяем платежи пользователя
    payments_count, access_count = check_user_payments(user_id)
    
    print(f"\n📊 Результат проверки:")
    print(f"   • Платежей: {payments_count}")
    print(f"   • Записей доступа: {access_count}")
    
    if payments_count > 0 and access_count > 0:
        print("\n✅ Пользователь имеет платежи и доступ")
        print("Проблема может быть в том, что уведомления не отправляются")
        
        # Отправляем уведомление
        notification_sent = await send_notification_to_user(user_id)
        
        if notification_sent:
            print("\n🎉 Уведомление отправлено!")
            print("Пользователь должен получить кнопки доступа")
        else:
            print("\n❌ Не удалось отправить уведомление")
            print("Проверьте настройки бота и логи")
    else:
        print("\n⚠️ Проблемы с данными пользователя")
        print("Проверьте базу данных")
    
    print("\n💡 Рекомендации:")
    print("1. Запустите бота: python run_no_webhook.py")
    print("2. Проверьте логи на ошибки")
    print("3. Убедитесь, что периодическая проверка работает")

if __name__ == "__main__":
    asyncio.run(main())
