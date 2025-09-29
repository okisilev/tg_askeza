#!/usr/bin/env python3
"""
Запуск бота и проверка автоматической обработки
"""

import asyncio
import logging
import threading
import time
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

def check_payments_sync():
    """Синхронная проверка платежей"""
    print("🔍 Проверка платежей")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Проверяем pending платежи
        with db.conn.cursor() as cursor:
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
        with db.conn.cursor() as cursor:
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
        print(f"❌ Ошибка при проверке платежей: {e}")
        return 0, 0

async def process_successful_payment(user_id: int, payment_id: str, payment_type: str, amount: float):
    """Обработка успешного платежа"""
    print(f"💳 Обработка платежа {payment_id} для пользователя {user_id}")
    
    try:
        db = Database()
        channel_manager = ChannelManager()
        
        # Предоставляем доступ
        if db.grant_access(user_id, payment_type):
            print(f"✅ Доступ предоставлен пользователю {user_id}")
        else:
            print(f"❌ Не удалось предоставить доступ пользователю {user_id}")
            return False
        
        # Добавляем пользователя в каналы
        try:
            success = await channel_manager.grant_access_to_user(user_id, payment_type)
            if success:
                print(f"✅ Пользователь {user_id} добавлен в каналы")
            else:
                print(f"⚠️ Не удалось добавить пользователя {user_id} в каналы")
        except Exception as e:
            print(f"⚠️ Ошибка при добавлении в каналы: {e}")
        
        # Отправляем уведомление
        try:
            from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
            
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
            
        except Exception as e:
            print(f"❌ Ошибка при отправке уведомления: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при обработке платежа: {e}")
        return False

async def check_and_process_payments():
    """Проверка и обработка платежей"""
    print("🔄 Проверка и обработка платежей")
    print("=" * 50)
    
    try:
        db = Database()
        yookassa_client = YooKassaClient()
        
        # Получаем все pending платежи
        with db.conn.cursor() as cursor:
            cursor.execute('''
                SELECT user_id, yookassa_payment_id, payment_type, amount, created_at 
                FROM payments 
                WHERE status = 'pending'
                ORDER BY created_at DESC
            ''')
            pending_payments = cursor.fetchall()
        
        if not pending_payments:
            print("✅ Pending платежей не найдено")
            return
        
        print(f"⏳ Найдено {len(pending_payments)} pending платежей")
        
        # Проверяем каждый платеж
        for payment in pending_payments:
            user_id, payment_id, payment_type, amount, created_at = payment
            
            try:
                # Проверяем статус платежа в ЮKassa
                payment_info = yookassa_client.get_payment_status(payment_id)
                
                if payment_info and payment_info.get('status') == 'succeeded':
                    print(f"✅ Платеж {payment_id} успешен")
                    
                    # Обновляем статус в базе данных
                    with db.conn.cursor() as cursor:
                        cursor.execute('''
                            UPDATE payments 
                            SET status = 'succeeded', paid_at = CURRENT_TIMESTAMP 
                            WHERE yookassa_payment_id = ?
                        ''', (payment_id,))
                        db.conn.commit()
                    
                    # Обрабатываем успешный платеж
                    await process_successful_payment(user_id, payment_id, payment_type, amount)
                    
                elif payment_info and payment_info.get('status') == 'canceled':
                    print(f"❌ Платеж {payment_id} отменен")
                    
                    # Обновляем статус в базе данных
                    with db.conn.cursor() as cursor:
                        cursor.execute('''
                            UPDATE payments 
                            SET status = 'canceled' 
                            WHERE yookassa_payment_id = ?
                        ''', (payment_id,))
                        db.conn.commit()
                    
                else:
                    print(f"⏳ Платеж {payment_id} все еще pending")
                    
            except Exception as e:
                print(f"❌ Ошибка при проверке платежа {payment_id}: {e}")
        
    except Exception as e:
        print(f"❌ Ошибка при проверке платежей: {e}")

def periodic_payment_check():
    """Периодическая проверка платежей"""
    print("🔄 Запуск периодической проверки платежей")
    print("=" * 50)
    
    while True:
        try:
            print(f"🔍 Проверка платежей в {datetime.now().strftime('%H:%M:%S')}")
            
            # Создаем новый event loop для этого потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Запускаем проверку
            loop.run_until_complete(check_and_process_payments())
            
            # Закрываем event loop
            loop.close()
            
            print("✅ Проверка завершена, ждем 5 минут...")
            time.sleep(300)  # Проверяем каждые 5 минут
            
        except Exception as e:
            print(f"❌ Ошибка в периодической проверке: {e}")
            time.sleep(60)  # При ошибке ждем 1 минуту

def main():
    """Основная функция"""
    print("🚀 Запуск бота и проверка автоматической обработки")
    print("=" * 50)
    
    # Проверяем текущее состояние
    pending_count, without_access_count = check_payments_sync()
    
    print(f"\n📊 Текущее состояние:")
    print(f"   • Pending платежей: {pending_count}")
    print(f"   • Платежей без доступа: {without_access_count}")
    
    if without_access_count > 0:
        print("\n⚠️ Обнаружены платежи без доступа!")
        print("Рекомендации:")
        print("1. Запустите бота: python run_no_webhook.py")
        print("2. Или исправьте вручную: python fix_all_payments.py")
    else:
        print("\n✅ Все платежи обработаны корректно")
    
    print("\n💡 Для автоматической обработки запустите:")
    print("   python run_no_webhook.py")

if __name__ == "__main__":
    main()
