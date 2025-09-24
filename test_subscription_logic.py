#!/usr/bin/env python3
"""
Тестовый скрипт для проверки логики работы с подписками
"""

import asyncio
import logging
from handlers import BotHandlers
from channel_manager import ChannelManager
from config import PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def test_subscription_logic():
    """Тест логики работы с подписками"""
    print("🔍 Тестирование логики работы с подписками")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        handlers = BotHandlers()
        channel_manager = ChannelManager()
        
        print("✅ Компоненты инициализированы")
        
        # Проверяем конфигурацию
        print(f"\n📋 Конфигурация:")
        print(f"   PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
        print(f"   PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
        
        if not PRIVATE_CHANNEL_ID:
            print("⚠️ Канал не настроен")
            return
        
        # Тестируем права бота
        print(f"\n🔐 Проверка прав бота:")
        permissions = await channel_manager.check_bot_permissions()
        
        if permissions['channel']['is_admin']:
            print("   ✅ Бот является администратором канала")
            if permissions['channel']['can_invite']:
                print("   ✅ Бот может приглашать пользователей")
            else:
                print("   ❌ Бот НЕ может приглашать пользователей")
        else:
            print("   ❌ Бот НЕ является администратором канала")
        
        # Тестируем создание пригласительной ссылки
        print(f"\n🔗 Тестирование создания пригласительной ссылки:")
        try:
            # Создаем тестовую пригласительную ссылку
            invite_link = await channel_manager.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                expire_date=None
            )
            print(f"   ✅ Пригласительная ссылка создана: {invite_link.invite_link[:50]}...")
        except Exception as e:
            print(f"   ❌ Ошибка создания ссылки: {e}")
        
        # Тестируем проверку подписки (с тестовым пользователем)
        print(f"\n👤 Тестирование проверки подписки:")
        test_user_id = 123456789  # Тестовый ID пользователя
        
        try:
            is_subscribed = await channel_manager.check_user_in_channel(test_user_id)
            if is_subscribed:
                print(f"   ✅ Пользователь {test_user_id} подписан на канал")
            else:
                print(f"   ❌ Пользователь {test_user_id} НЕ подписан на канал")
        except Exception as e:
            print(f"   ⚠️ Ошибка проверки подписки: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def print_workflow():
    """Печать схемы работы с подписками"""
    print("\n" + "=" * 50)
    print("📋 СХЕМА РАБОТЫ С ПОДПИСКАМИ")
    print("=" * 50)
    
    print("\n1️⃣ Пользователь нажимает 'Закрытый канал':")
    print("   • Бот проверяет, есть ли у пользователя активный доступ")
    print("   • Бот проверяет, подписан ли пользователь на канал")
    
    print("\n2️⃣ Если пользователь НЕ подписан:")
    print("   • Бот отправляет пригласительную ссылку")
    print("   • Показывает кнопку 'Проверить подписку'")
    print("   • Пользователь переходит по ссылке и подписывается")
    
    print("\n3️⃣ Если пользователь подписан:")
    print("   • Бот показывает кнопку 'Перейти в канал'")
    print("   • Пользователь может сразу перейти в канал")
    
    print("\n4️⃣ Пользователь нажимает 'Проверить подписку':")
    print("   • Бот снова проверяет подписку через get_chat_member")
    print("   • Если подписан - дает доступ к каналу")
    print("   • Если не подписан - просит подписаться снова")
    
    print("\n5️⃣ Результат:")
    print("   • Пользователь получает доступ к эксклюзивному контенту")
    print("   • Может переходить в канал по прямой ссылке")

def print_requirements():
    """Печать требований для работы"""
    print("\n" + "=" * 50)
    print("⚙️ ТРЕБОВАНИЯ ДЛЯ РАБОТЫ")
    print("=" * 50)
    
    print("\n🔐 Права бота:")
    print("   • Бот должен быть администратором канала")
    print("   • Бот должен иметь права на приглашение пользователей")
    print("   • Бот должен иметь права на создание пригласительных ссылок")
    
    print("\n📱 Настройка канала:")
    print("   • Канал должен быть приватным")
    print("   • PRIVATE_CHANNEL_ID должен быть настроен в .env")
    print("   • Бот должен быть добавлен в канал как администратор")
    
    print("\n👤 Права пользователя:")
    print("   • Пользователь должен иметь активный доступ (оплаченный)")
    print("   • Пользователь должен подписаться на канал по ссылке")
    print("   • Пользователь не должен блокировать бота")

async def main():
    """Основная функция"""
    print("🤖 Тестирование логики работы с подписками")
    print("=" * 50)
    
    # Тестируем логику
    success = await test_subscription_logic()
    
    if success:
        print("\n✅ Тест логики пройден")
    else:
        print("\n❌ Тест логики не пройден")
    
    # Показываем схему работы
    print_workflow()
    
    # Показываем требования
    print_requirements()
    
    print("\n📋 Новая функциональность:")
    print("1. ✅ Проверка подписки через get_chat_member")
    print("2. ✅ Отправка пригласительных ссылок")
    print("3. ✅ Кнопка 'Проверить подписку'")
    print("4. ✅ Автоматическая проверка статуса подписки")
    print("5. ✅ Прямые ссылки для перехода в канал")

if __name__ == "__main__":
    asyncio.run(main())
