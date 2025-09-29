#!/usr/bin/env python3
"""
Тестовый скрипт для проверки доступа к конкретному каналу
PRIVATE_CHANNEL_ID=-1002806695160
"""

import asyncio
import logging
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_specific_channel_access():
    """Тест доступа к конкретному каналу"""
    print("📺 Тестирование доступа к каналу PRIVATE_CHANNEL_ID=-1002806695160")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Проверяем настройки
        print(f"🔧 Настройки:")
        print(f"   • BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
        print(f"   • PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
        print(f"   • PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
        
        if not PRIVATE_CHANNEL_ID:
            print("❌ PRIVATE_CHANNEL_ID не настроен")
            return False
        
        # Проверяем права бота в канале
        print(f"\n🔐 Проверяем права бота в канале {PRIVATE_CHANNEL_ID}...")
        
        try:
            # Инициализируем бота если нужно
            if not channel_manager.bot._initialized:
                await channel_manager.bot.initialize()
            
            # Проверяем, является ли бот администратором канала
            bot_member = await channel_manager.bot.get_chat_member(
                chat_id=PRIVATE_CHANNEL_ID, 
                user_id=channel_manager.bot.id
            )
            
            print(f"✅ Статус бота в канале: {bot_member.status}")
            
            if bot_member.status in ['administrator', 'creator']:
                print("✅ Бот является администратором канала")
                
                # Проверяем права на приглашение
                try:
                    invite_link = await channel_manager.bot.create_chat_invite_link(
                        chat_id=PRIVATE_CHANNEL_ID,
                        member_limit=1,
                        expire_date=None
                    )
                    print("✅ Бот может создавать пригласительные ссылки")
                    print(f"🔗 Пример ссылки: {invite_link.invite_link}")
                    
                except Exception as e:
                    print(f"❌ Бот не может создавать пригласительные ссылки: {e}")
                    
            else:
                print("❌ Бот НЕ является администратором канала")
                print("🔧 Нужно добавить бота как администратора с правами на приглашение")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при проверке прав бота: {e}")
            return False
        
        # Проверяем информацию о канале
        print(f"\n📋 Информация о канале:")
        try:
            chat = await channel_manager.bot.get_chat(chat_id=PRIVATE_CHANNEL_ID)
            print(f"   • Название: {chat.title}")
            print(f"   • Тип: {chat.type}")
            print(f"   • Описание: {chat.description or 'Нет описания'}")
            print(f"   • Постоянная ссылка: {chat.invite_link or 'Нет постоянной ссылки'}")
            
        except Exception as e:
            print(f"❌ Ошибка при получении информации о канале: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

async def test_user_access_to_channel(user_id: int):
    """Тест доступа пользователя к каналу"""
    print(f"\n👤 Тестирование доступа пользователя {user_id} к каналу")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Проверяем, есть ли пользователь в канале
        in_channel = await channel_manager.check_user_in_channel(user_id)
        print(f"📺 Пользователь в канале: {in_channel}")
        
        if not in_channel:
            print("🔄 Пытаемся добавить пользователя в канал...")
            
            # Пытаемся добавить пользователя в канал
            success = await channel_manager.add_user_to_channel(user_id)
            
            if success:
                print("✅ Пользователь успешно добавлен в канал")
                
                # Проверяем еще раз
                in_channel_after = await channel_manager.check_user_in_channel(user_id)
                print(f"📺 Пользователь в канале после добавления: {in_channel_after}")
                
            else:
                print("❌ Не удалось добавить пользователя в канал")
                return False
        else:
            print("✅ Пользователь уже в канале")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке доступа пользователя: {e}")
        return False

def test_database_access(user_id: int):
    """Тест доступа в базе данных"""
    print(f"\n💾 Тестирование доступа в базе данных для пользователя {user_id}")
    print("=" * 50)
    
    try:
        db = Database()
        
        # Проверяем пользователя
        user = db.get_user(user_id)
        if user:
            print(f"✅ Пользователь найден: {user[1]}")
        else:
            print("❌ Пользователь не найден в базе данных")
            return False
        
        # Проверяем доступ
        user_access = db.get_user_access(user_id)
        if user_access:
            print(f"✅ Доступ найден: {user_access[2]} (активен: {user_access[5]})")
        else:
            print("❌ Активный доступ не найден")
            return False
        
        # Проверяем платежи
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, status, created_at 
                FROM payments 
                WHERE user_id = ? AND status = 'succeeded'
                ORDER BY created_at DESC
                LIMIT 1
            ''', (user_id,))
            payment = cursor.fetchone()
        
        if payment:
            print(f"✅ Успешный платеж найден: {payment[0]} ({payment[2]})")
        else:
            print("❌ Успешных платежей не найдено")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def print_setup_instructions():
    """Печать инструкций по настройке"""
    print("\n" + "=" * 50)
    print("🔧 ИНСТРУКЦИИ ПО НАСТРОЙКЕ")
    print("=" * 50)
    
    print("\n1️⃣ Настройте переменные окружения:")
    print("   • BOT_TOKEN - токен бота")
    print("   • PRIVATE_CHANNEL_ID=-1002806695160")
    print("   • PRIVATE_CHAT_ID - ID чата (если нужен)")
    
    print("\n2️⃣ Добавьте бота в канал как администратора:")
    print("   • Пригласите бота в канал")
    print("   • Сделайте бота администратором")
    print("   • Дайте права на приглашение пользователей")
    
    print("\n3️⃣ Проверьте права бота:")
    print("   • Бот должен быть администратором")
    print("   • У бота должны быть права на приглашение")
    print("   • Бот должен иметь права на добавление участников")
    
    print("\n4️⃣ Проверьте настройки канала:")
    print("   • Канал должен быть приватным")
    print("   • У бота должны быть права администратора")
    print("   • Проверьте, что канал существует")

async def main():
    """Основная функция"""
    user_id = 431292182  # Тестовый пользователь из логов
    
    print("🧪 Тестирование доступа к каналу PRIVATE_CHANNEL_ID=-1002806695160")
    print("=" * 50)
    
    # Тестируем настройки канала
    channel_ok = await test_specific_channel_access()
    
    if channel_ok:
        print("✅ Настройки канала работают")
    else:
        print("❌ Проблемы с настройками канала")
        print_setup_instructions()
        return
    
    # Тестируем базу данных
    db_ok = test_database_access(user_id)
    
    if db_ok:
        print("✅ База данных работает")
    else:
        print("❌ Проблемы с базой данных")
        return
    
    # Тестируем доступ пользователя
    access_ok = await test_user_access_to_channel(user_id)
    
    if access_ok:
        print("✅ Доступ пользователя работает")
    else:
        print("❌ Проблемы с доступом пользователя")
    
    print("\n📋 Рекомендации:")
    print("1. Убедитесь, что бот является администратором канала")
    print("2. Проверьте, что у бота есть права на приглашение")
    print("3. Запустите бота и протестируйте кнопку 'Закрытый канал'")

if __name__ == "__main__":
    asyncio.run(main())
