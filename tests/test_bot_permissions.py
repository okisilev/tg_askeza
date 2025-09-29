#!/usr/bin/env python3
"""
Тестовый скрипт для проверки прав бота в каналах и чатах
"""

import asyncio
import logging
from channel_manager import ChannelManager
from config import PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_bot_permissions():
    """Тест прав бота в каналах и чатах"""
    print("🔍 Проверка прав бота в каналах и чатах")
    print("=" * 50)
    
    try:
        channel_manager = ChannelManager()
        permissions = await channel_manager.check_bot_permissions()
        
        # Проверяем права в канале
        print("\n📺 Канал:")
        if PRIVATE_CHANNEL_ID:
            print(f"   ID: {PRIVATE_CHANNEL_ID}")
            if permissions['channel']['is_admin']:
                print("   ✅ Бот является администратором")
                if permissions['channel']['can_invite']:
                    print("   ✅ Бот может приглашать пользователей")
                else:
                    print("   ❌ Бот НЕ может приглашать пользователей")
                    if permissions['channel']['error']:
                        print(f"   Ошибка: {permissions['channel']['error']}")
            else:
                print("   ❌ Бот НЕ является администратором")
                if permissions['channel']['error']:
                    print(f"   Ошибка: {permissions['channel']['error']}")
        else:
            print("   ⚠️ Канал не настроен")
        
        # Проверяем права в чате
        print("\n💬 Чат:")
        if PRIVATE_CHAT_ID:
            print(f"   ID: {PRIVATE_CHAT_ID}")
            if permissions['chat']['is_admin']:
                print("   ✅ Бот является администратором")
                if permissions['chat']['can_invite']:
                    print("   ✅ Бот может приглашать пользователей")
                else:
                    print("   ❌ Бот НЕ может приглашать пользователей")
                    if permissions['chat']['error']:
                        print(f"   Ошибка: {permissions['chat']['error']}")
            else:
                print("   ❌ Бот НЕ является администратором")
                if permissions['chat']['error']:
                    print(f"   Ошибка: {permissions['chat']['error']}")
        else:
            print("   ⚠️ Чат не настроен")
        
        # Общие рекомендации
        print("\n📋 Рекомендации:")
        
        if PRIVATE_CHANNEL_ID and not permissions['channel']['is_admin']:
            print("   ❌ Для канала:")
            print("      1. Добавьте бота в канал как администратора")
            print("      2. Дайте боту права на приглашение пользователей")
            print("      3. Убедитесь, что бот может создавать пригласительные ссылки")
        
        if PRIVATE_CHAT_ID and not permissions['chat']['is_admin']:
            print("   ❌ Для чата:")
            print("      1. Добавьте бота в чат как администратора")
            print("      2. Дайте боту права на приглашение пользователей")
            print("      3. Убедитесь, что бот может создавать пригласительные ссылки")
        
        if permissions['channel']['is_admin'] and permissions['channel']['can_invite']:
            print("   ✅ Канал настроен правильно")
        
        if permissions['chat']['is_admin'] and permissions['chat']['can_invite']:
            print("   ✅ Чат настроен правильно")
        
        return permissions
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return None

def print_setup_instructions():
    """Печать инструкций по настройке"""
    print("\n" + "=" * 50)
    print("📖 ИНСТРУКЦИИ ПО НАСТРОЙКЕ ПРАВ БОТА")
    print("=" * 50)
    
    print("\n1️⃣ Добавление бота в канал/чат:")
    print("   • Откройте канал/чат в Telegram")
    print("   • Нажмите на название канала/чата")
    print("   • Выберите 'Управление' → 'Администраторы'")
    print("   • Нажмите 'Добавить администратора'")
    print("   • Найдите вашего бота по username")
    print("   • Добавьте бота как администратора")
    
    print("\n2️⃣ Настройка прав бота:")
    print("   • В разделе 'Права администратора' включите:")
    print("     ✅ Приглашать пользователей")
    print("     ✅ Добавлять участников")
    print("     ✅ Удалять участников (опционально)")
    print("     ✅ Блокировать пользователей (опционально)")
    
    print("\n3️⃣ Проверка настроек:")
    print("   • Убедитесь, что бот отображается в списке администраторов")
    print("   • Проверьте, что у бота есть права на приглашение")
    print("   • Запустите этот тест снова для проверки")
    
    print("\n4️⃣ Настройка .env файла:")
    print("   PRIVATE_CHANNEL_ID=@your_private_channel")
    print("   PRIVATE_CHAT_ID=@your_private_chat")
    print("   # Или используйте числовые ID:")
    print("   PRIVATE_CHANNEL_ID=-1001234567890")
    print("   PRIVATE_CHAT_ID=-1001234567890")

async def main():
    """Основная функция"""
    print("🤖 Тестирование прав бота")
    print("=" * 50)
    
    # Проверяем конфигурацию
    print(f"PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
    print(f"PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
    
    if not PRIVATE_CHANNEL_ID and not PRIVATE_CHAT_ID:
        print("⚠️ Ни канал, ни чат не настроены в .env файле")
        print_setup_instructions()
        return
    
    # Тестируем права
    permissions = await test_bot_permissions()
    
    if permissions:
        # Проверяем, все ли настроено правильно
        channel_ok = not PRIVATE_CHANNEL_ID or (permissions['channel']['is_admin'] and permissions['channel']['can_invite'])
        chat_ok = not PRIVATE_CHAT_ID or (permissions['chat']['is_admin'] and permissions['chat']['can_invite'])
        
        if channel_ok and chat_ok:
            print("\n✅ Все права настроены правильно!")
            print("Бот может добавлять и удалять пользователей из каналов и чатов.")
        else:
            print("\n❌ Требуется настройка прав бота")
            print_setup_instructions()
    else:
        print("\n❌ Не удалось проверить права бота")
        print_setup_instructions()

if __name__ == "__main__":
    asyncio.run(main())
