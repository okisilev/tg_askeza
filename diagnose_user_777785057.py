#!/usr/bin/env python3
"""
Диагностический скрипт для пользователя 777785057
"""

import asyncio
import logging
from database import Database
from channel_manager import ChannelManager
from config import PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def diagnose_user(user_id: int):
    """Диагностика пользователя"""
    print(f"🔍 Диагностика пользователя {user_id}")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        db = Database()
        channel_manager = ChannelManager()
        
        print("✅ Компоненты инициализированы")
        
        # 1. Проверяем данные пользователя в базе
        print(f"\n📊 Данные пользователя в базе данных:")
        user = db.get_user(user_id)
        if user:
            print(f"   ✅ Пользователь найден в базе")
            print(f"   ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   First Name: {user[2]}")
            print(f"   Last Name: {user[3]}")
            print(f"   Created: {user[4]}")
        else:
            print(f"   ❌ Пользователь НЕ найден в базе данных")
            return False
        
        # 2. Проверяем доступ пользователя
        print(f"\n🔐 Проверка доступа пользователя:")
        user_access = db.get_user_access(user_id)
        if user_access:
            print(f"   ✅ У пользователя есть активный доступ")
            print(f"   Тип доступа: {user_access[2]}")
            print(f"   Дата начала: {user_access[3]}")
            print(f"   Дата окончания: {user_access[4]}")
            print(f"   Активен: {user_access[5]}")
        else:
            print(f"   ❌ У пользователя НЕТ активного доступа")
            return False
        
        # 3. Проверяем платежи пользователя
        print(f"\n💳 История платежей пользователя:")
        payments = db.get_user_payments(user_id)
        if payments:
            print(f"   ✅ Найдено {len(payments)} платежей:")
            for payment in payments:
                print(f"   - ID: {payment[0]}")
                print(f"     Тип: {payment[2]}")
                print(f"     Сумма: {payment[3]}₽")
                print(f"     Статус: {payment[4]}")
                print(f"     Дата: {payment[5]}")
                if payment[6]:  # paid_at
                    print(f"     Оплачен: {payment[6]}")
        else:
            print(f"   ❌ Платежи не найдены")
        
        # 4. Проверяем подписку на канал
        print(f"\n📺 Проверка подписки на канал:")
        if PRIVATE_CHANNEL_ID:
            try:
                is_subscribed = await channel_manager.check_user_in_channel(user_id)
                if is_subscribed:
                    print(f"   ✅ Пользователь подписан на канал {PRIVATE_CHANNEL_ID}")
                else:
                    print(f"   ❌ Пользователь НЕ подписан на канал {PRIVATE_CHANNEL_ID}")
            except Exception as e:
                print(f"   ⚠️ Ошибка проверки подписки: {e}")
        else:
            print(f"   ⚠️ PRIVATE_CHANNEL_ID не настроен")
        
        # 5. Проверяем подписку на чат
        print(f"\n💬 Проверка подписки на чат:")
        if PRIVATE_CHAT_ID:
            try:
                is_in_chat = await channel_manager.check_user_in_chat(user_id)
                if is_in_chat:
                    print(f"   ✅ Пользователь в чате {PRIVATE_CHAT_ID}")
                else:
                    print(f"   ❌ Пользователь НЕ в чате {PRIVATE_CHAT_ID}")
            except Exception as e:
                print(f"   ⚠️ Ошибка проверки чата: {e}")
        else:
            print(f"   ⚠️ PRIVATE_CHAT_ID не настроен")
        
        # 6. Проверяем права бота
        print(f"\n🤖 Проверка прав бота:")
        permissions = await channel_manager.check_bot_permissions()
        
        if PRIVATE_CHANNEL_ID:
            if permissions['channel']['is_admin']:
                print(f"   ✅ Бот является администратором канала")
                if permissions['channel']['can_invite']:
                    print(f"   ✅ Бот может приглашать пользователей")
                else:
                    print(f"   ❌ Бот НЕ может приглашать пользователей")
            else:
                print(f"   ❌ Бот НЕ является администратором канала")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

async def fix_user_access(user_id: int):
    """Попытка исправить доступ пользователя"""
    print(f"\n🔧 Попытка исправить доступ пользователя {user_id}")
    print("=" * 50)
    
    try:
        db = Database()
        channel_manager = ChannelManager()
        
        # 1. Проверяем, есть ли у пользователя доступ
        user_access = db.get_user_access(user_id)
        if not user_access:
            print("❌ У пользователя нет активного доступа в базе данных")
            return False
        
        # 2. Проверяем подписку на канал
        is_subscribed = await channel_manager.check_user_in_channel(user_id)
        if is_subscribed:
            print("✅ Пользователь уже подписан на канал")
            return True
        
        # 3. Пытаемся отправить пригласительную ссылку
        print("📧 Отправляем пригласительную ссылку...")
        success = await channel_manager.send_channel_invite(user_id)
        
        if success:
            print("✅ Пригласительная ссылка отправлена")
            print("Пользователь должен подписаться по ссылке и нажать 'Проверить подписку'")
        else:
            print("❌ Не удалось отправить пригласительную ссылку")
            print("Возможные причины:")
            print("- Бот не является администратором канала")
            print("- У бота нет прав на приглашение пользователей")
            print("- Пользователь заблокировал бота")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка при исправлении доступа: {e}")
        return False

async def main():
    """Основная функция"""
    user_id = 777785057
    
    print("🚨 ДИАГНОСТИКА ПРОБЛЕМЫ С ПОЛЬЗОВАТЕЛЕМ")
    print("=" * 50)
    
    # Диагностируем пользователя
    success = await diagnose_user(user_id)
    
    if success:
        print("\n🔧 Попытка исправления...")
        fix_success = await fix_user_access(user_id)
        
        if fix_success:
            print("\n✅ Проблема решена!")
        else:
            print("\n❌ Не удалось автоматически решить проблему")
            print("\n📋 Рекомендации:")
            print("1. Проверьте, что бот является администратором канала")
            print("2. Убедитесь, что у бота есть права на приглашение пользователей")
            print("3. Проверьте, что пользователь не заблокировал бота")
            print("4. Попробуйте отправить пригласительную ссылку вручную")
    else:
        print("\n❌ Не удалось провести диагностику")

if __name__ == "__main__":
    asyncio.run(main())
