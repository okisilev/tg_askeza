#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправления доступа к каналу
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

async def test_bot_initialization():
    """Тест инициализации бота"""
    print("🤖 Тестирование инициализации бота")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Проверяем, что бот создан
        print(f"✅ Бот создан: {channel_manager.bot}")
        print(f"✅ Токен настроен: {'Да' if BOT_TOKEN else 'Нет'}")
        
        # Проверяем инициализацию
        if not channel_manager.bot._initialized:
            print("🔄 Инициализируем бота...")
            await channel_manager.bot.initialize()
            print("✅ Бот инициализирован")
        else:
            print("✅ Бот уже инициализирован")
        
        # Проверяем ID бота
        bot_id = channel_manager.bot.id
        print(f"✅ ID бота: {bot_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации бота: {e}")
        return False

async def test_bot_permissions():
    """Тест прав бота"""
    print("\n🔐 Тестирование прав бота")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Проверяем права бота
        permissions = await channel_manager.check_bot_permissions()
        
        print("📺 Права в канале:")
        print(f"   - Администратор: {permissions['channel']['is_admin']}")
        print(f"   - Может приглашать: {permissions['channel']['can_invite']}")
        if permissions['channel']['error']:
            print(f"   - Ошибка: {permissions['channel']['error']}")
        
        print("\n💬 Права в чате:")
        print(f"   - Администратор: {permissions['chat']['is_admin']}")
        print(f"   - Может приглашать: {permissions['chat']['can_invite']}")
        if permissions['chat']['error']:
            print(f"   - Ошибка: {permissions['chat']['error']}")
        
        return permissions
        
    except Exception as e:
        print(f"❌ Ошибка при проверке прав: {e}")
        return None

async def test_channel_access(user_id: int):
    """Тест доступа к каналу"""
    print(f"\n📺 Тестирование доступа к каналу для пользователя {user_id}")
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
        print(f"❌ Ошибка при проверке доступа: {e}")
        return False, False

async def test_add_user_to_channel(user_id: int):
    """Тест добавления пользователя в канал"""
    print(f"\n➕ Тестирование добавления пользователя {user_id} в канал")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        
        # Пытаемся добавить пользователя в канал
        success = await channel_manager.add_user_to_channel(user_id)
        
        if success:
            print("✅ Пользователь успешно добавлен в канал")
        else:
            print("❌ Не удалось добавить пользователя в канал")
        
        return success
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
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

def print_troubleshooting():
    """Печать инструкций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 УСТРАНЕНИЕ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте настройки:")
    print(f"   • BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
    print(f"   • PRIVATE_CHANNEL_ID: {'Настроен' if PRIVATE_CHANNEL_ID else 'НЕ настроен'}")
    print(f"   • PRIVATE_CHAT_ID: {'Настроен' if PRIVATE_CHAT_ID else 'НЕ настроен'}")
    
    print("\n2️⃣ Проверьте права бота:")
    print("   • Бот должен быть администратором канала")
    print("   • У бота должны быть права на приглашение пользователей")
    print("   • Проверьте, что канал существует и доступен")
    
    print("\n3️⃣ Проверьте пользователя:")
    print("   • Пользователь должен быть в базе данных")
    print("   • Должен быть активный доступ")
    print("   • Должен быть успешный платеж")
    
    print("\n4️⃣ Проверьте логи:")
    print("   • Ищите ошибки инициализации бота")
    print("   • Проверьте ошибки доступа к каналу")
    print("   • Убедитесь, что все компоненты работают")

async def main():
    """Основная функция"""
    user_id = 431292182  # Тестовый пользователь из логов
    
    print("🧪 Тестирование исправления доступа к каналу")
    print("=" * 50)
    
    # Тестируем инициализацию бота
    init_ok = await test_bot_initialization()
    
    if init_ok:
        print("✅ Инициализация бота работает")
    else:
        print("❌ Проблемы с инициализацией бота")
        return
    
    # Тестируем права бота
    permissions = await test_bot_permissions()
    
    if permissions:
        print("✅ Проверка прав работает")
    else:
        print("❌ Проблемы с проверкой прав")
    
    # Тестируем базу данных
    db_ok = test_database_access(user_id)
    
    if db_ok:
        print("✅ База данных работает")
    else:
        print("❌ Проблемы с базой данных")
    
    # Тестируем доступ к каналу
    in_channel, in_chat = await test_channel_access(user_id)
    
    print(f"📺 В канале: {in_channel}")
    print(f"💬 В чате: {in_chat}")
    
    # Тестируем добавление в канал
    if not in_channel:
        add_ok = await test_add_user_to_channel(user_id)
        
        if add_ok:
            print("✅ Добавление в канал работает")
        else:
            print("❌ Проблемы с добавлением в канал")
    
    # Показываем инструкции по устранению неполадок
    print_troubleshooting()
    
    print("\n📋 Рекомендации:")
    print("1. Запустите бота и протестируйте кнопку 'Закрытый канал'")
    print("2. Проверьте логи на наличие ошибок")
    print("3. Убедитесь, что бот имеет права администратора")
    print("4. Проверьте, что пользователь имеет активный доступ")

if __name__ == "__main__":
    asyncio.run(main())
