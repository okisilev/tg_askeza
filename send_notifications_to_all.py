#!/usr/bin/env python3
"""
Отправка уведомлений всем пользователям с успешными платежами
"""

import sqlite3
import asyncio
from datetime import datetime, timedelta
from config import DATABASE_PATH, BOT_TOKEN
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

async def send_notification_to_user(user_id: int, payment_type: str):
    """Отправка уведомления пользователю"""
    print(f"📧 Отправка уведомления пользователю {user_id}")
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
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
        
        print(f"✅ Уведомление с кнопками отправлено пользователю {user_id}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False

async def send_notifications_to_all():
    """Отправка уведомлений всем пользователям с успешными платежами"""
    print("📧 Отправка уведомлений всем пользователям с успешными платежами")
    print("=" * 50)
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Получаем всех пользователей с успешными платежами
        cursor.execute('''
            SELECT DISTINCT p.user_id, p.payment_type, p.amount, p.created_at
            FROM payments p
            WHERE p.status = 'succeeded'
            ORDER BY p.created_at DESC
        ''')
        users_with_payments = cursor.fetchall()
        
        if not users_with_payments:
            print("❌ Пользователей с успешными платежами не найдено")
            return
        
        print(f"📋 Найдено {len(users_with_payments)} пользователей с успешными платежами:")
        for user in users_with_payments:
            print(f"   • User: {user[0]}")
            print(f"     Type: {user[1]}")
            print(f"     Amount: {user[2]}₽")
            print(f"     Created: {user[3]}")
            print()
        
        # Отправляем уведомления
        success_count = 0
        error_count = 0
        
        for user in users_with_payments:
            user_id, payment_type, amount, created_at = user
            
            try:
                success = await send_notification_to_user(user_id, payment_type)
                if success:
                    success_count += 1
                else:
                    error_count += 1
                    
                # Небольшая задержка между отправками
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Ошибка при отправке уведомления пользователю {user_id}: {e}")
                error_count += 1
        
        print(f"\n📊 Результат отправки уведомлений:")
        print(f"   • Всего пользователей: {len(users_with_payments)}")
        print(f"   • Успешно отправлено: {success_count}")
        print(f"   • Ошибок: {error_count}")
        
        if success_count > 0:
            print(f"\n🎉 {success_count} пользователей получили кнопки доступа!")
        else:
            print("\n❌ Не удалось отправить ни одного уведомления")
            print("Проверьте настройки бота и логи")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомлений: {e}")

async def main():
    """Основная функция"""
    print("🚀 Отправка уведомлений всем пользователям")
    print("=" * 50)
    
    # Отправляем уведомления
    await send_notifications_to_all()
    
    print("\n💡 Рекомендации:")
    print("1. Запустите бота: python run_no_webhook.py")
    print("2. Проверьте логи на ошибки")
    print("3. Убедитесь, что периодическая проверка работает")

if __name__ == "__main__":
    asyncio.run(main())
