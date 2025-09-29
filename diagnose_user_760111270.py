#!/usr/bin/env python3
"""
Диагностический скрипт для пользователя 760111270
Проверка платежа и доступа к каналу
"""

import asyncio
import logging
from datetime import datetime
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def check_user_payment(user_id: int):
    """Проверка платежа пользователя"""
    print(f"💳 Проверка платежа пользователя {user_id}")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Проверяем пользователя
        user = db.get_user(user_id)
        if user:
            print(f"✅ Пользователь найден: {user[1]} (@{user[2]})")
        else:
            print(f"❌ Пользователь {user_id} не найден в базе данных")
            return False
        
        # Проверяем платежи
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, payment_type, amount, status, created_at 
                FROM payments 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            payments = cursor.fetchall()
        
        if payments:
            print(f"📋 Найдено {len(payments)} платежей:")
            for payment in payments:
                print(f"   • ID: {payment[0]}")
                print(f"     Тип: {payment[1]}")
                print(f"     Сумма: {payment[2]}₽")
                print(f"     Статус: {payment[3]}")
                print(f"     Дата: {payment[4]}")
                print()
        else:
            print("❌ Платежей не найдено")
            return False
        
        # Проверяем успешные платежи
        successful_payments = [p for p in payments if p[3] == 'succeeded']
        if successful_payments:
            print(f"✅ Успешных платежей: {len(successful_payments)}")
            for payment in successful_payments:
                print(f"   • {payment[0]} - {payment[1]} - {payment[2]}₽ - {payment[4]}")
        else:
            print("❌ Успешных платежей не найдено")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке платежа: {e}")
        return False

def check_user_access(user_id: int):
    """Проверка доступа пользователя"""
    print(f"\n🔐 Проверка доступа пользователя {user_id}")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Проверяем доступ
        user_access = db.get_user_access(user_id)
        if user_access:
            print(f"✅ Доступ найден:")
            print(f"   • Тип: {user_access[2]}")
            print(f"   • Создан: {user_access[3]}")
            print(f"   • Истекает: {user_access[4]}")
            print(f"   • Активен: {user_access[5]}")
            
            # Проверяем, не истек ли доступ
            if user_access[5] == 0:
                print("⚠️ Доступ неактивен (возможно, истек)")
                return False
            else:
                print("✅ Доступ активен")
                return True
        else:
            print("❌ Активный доступ не найден")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при проверке доступа: {e}")
        return False

async def check_channel_access(user_id: int):
    """Проверка доступа к каналу"""
    print(f"\n📺 Проверка доступа к каналу для пользователя {user_id}")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Проверяем, есть ли пользователь в канале
        in_channel = await channel_manager.check_user_in_channel(user_id)
        print(f"📺 Пользователь в канале: {in_channel}")
        
        # Проверяем, есть ли пользователь в чате
        in_chat = await channel_manager.check_user_in_chat(user_id)
        print(f"💬 Пользователь в чате: {in_chat}")
        
        return in_channel, in_chat
        
    except Exception as e:
        print(f"❌ Ошибка при проверке доступа к каналу: {e}")
        return False, False

async def simulate_payment_notification(user_id: int):
    """Симуляция уведомления о платеже"""
    print(f"\n📧 Симуляция уведомления о платеже для пользователя {user_id}")
    print("=" * 50)
    
    try:
        from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
        
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
        
        print("✅ Уведомление с кнопками отправлено")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления: {e}")
        return False

async def add_user_to_channel(user_id: int):
    """Добавление пользователя в канал"""
    print(f"\n➕ Добавление пользователя {user_id} в канал")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Добавляем пользователя в канал
        success = await channel_manager.add_user_to_channel(user_id)
        
        if success:
            print("✅ Пользователь успешно добавлен в канал")
        else:
            print("❌ Не удалось добавить пользователя в канал")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении в канал: {e}")
        return False

def print_troubleshooting():
    """Печать инструкций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 УСТРАНЕНИЕ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте платеж:")
    print("   • Убедитесь, что платеж имеет статус 'succeeded'")
    print("   • Проверьте, что платеж не был отменен")
    print("   • Убедитесь, что сумма платежа корректная")
    
    print("\n2️⃣ Проверьте доступ:")
    print("   • Убедитесь, что доступ активен")
    print("   • Проверьте, что доступ не истек")
    print("   • Убедитесь, что тип доступа правильный")
    
    print("\n3️⃣ Проверьте канал:")
    print("   • Убедитесь, что бот является администратором")
    print("   • Проверьте, что канал существует")
    print("   • Убедитесь, что пользователь не заблокирован")
    
    print("\n4️⃣ Проверьте уведомления:")
    print("   • Убедитесь, что бот может отправлять сообщения")
    print("   • Проверьте, что пользователь не заблокировал бота")
    print("   • Убедитесь, что кнопки обрабатываются")

async def main():
    """Основная функция"""
    user_id = 760111270
    
    print("🔍 Диагностика пользователя 760111270")
    print("=" * 50)
    
    # Проверяем платеж
    payment_ok = check_user_payment(user_id)
    
    if not payment_ok:
        print("❌ Проблемы с платежом")
        print_troubleshooting()
        return
    
    # Проверяем доступ
    access_ok = check_user_access(user_id)
    
    if not access_ok:
        print("❌ Проблемы с доступом")
        print_troubleshooting()
        return
    
    # Проверяем доступ к каналу
    in_channel, in_chat = await check_channel_access(user_id)
    
    print(f"\n📊 Результат проверки:")
    print(f"   • Платеж: {'✅' if payment_ok else '❌'}")
    print(f"   • Доступ: {'✅' if access_ok else '❌'}")
    print(f"   • В канале: {'✅' if in_channel else '❌'}")
    print(f"   • В чате: {'✅' if in_chat else '❌'}")
    
    # Если пользователь не в канале, пытаемся добавить
    if not in_channel:
        print("\n🔄 Пытаемся добавить пользователя в канал...")
        add_success = await add_user_to_channel(user_id)
        
        if add_success:
            print("✅ Пользователь добавлен в канал")
        else:
            print("❌ Не удалось добавить пользователя в канал")
    
    # Отправляем уведомление с кнопками
    print("\n📧 Отправляем уведомление с кнопками...")
    notification_success = await simulate_payment_notification(user_id)
    
    if notification_success:
        print("✅ Уведомление отправлено")
    else:
        print("❌ Не удалось отправить уведомление")
    
    print("\n📋 Рекомендации:")
    print("1. Проверьте, получил ли пользователь уведомление с кнопками")
    print("2. Убедитесь, что кнопки работают")
    print("3. Проверьте, что пользователь добавлен в канал")
    print("4. При необходимости запустите бота для автоматической обработки")

if __name__ == "__main__":
    asyncio.run(main())
