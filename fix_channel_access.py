#!/usr/bin/env python3
"""
Исправление проблемы с доступом к каналу
"""

import asyncio
import logging
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID
from telegram import Bot
from telegram.error import TelegramError

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def check_and_fix_channel_access():
    """Проверка и исправление доступа к каналу"""
    print("🔧 Проверка и исправление доступа к каналу")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.initialize()
        
        print(f"📺 Проверяем канал: {PRIVATE_CHANNEL_ID}")
        
        # Проверяем информацию о канале
        try:
            chat = await bot.get_chat(chat_id=PRIVATE_CHANNEL_ID)
            print(f"✅ Канал найден:")
            print(f"   • Название: {chat.title}")
            print(f"   • Тип: {chat.type}")
            print(f"   • Описание: {chat.description or 'Нет описания'}")
            
        except TelegramError as e:
            print(f"❌ Ошибка при получении информации о канале: {e}")
            return False
        
        # Проверяем статус бота в канале
        try:
            bot_member = await bot.get_chat_member(
                chat_id=PRIVATE_CHANNEL_ID, 
                user_id=bot.id
            )
            print(f"\n🤖 Статус бота в канале: {bot_member.status}")
            
            if bot_member.status in ['administrator', 'creator']:
                print("✅ Бот является администратором канала")
                
                # Проверяем права на приглашение
                try:
                    invite_link = await bot.create_chat_invite_link(
                        chat_id=PRIVATE_CHANNEL_ID,
                        member_limit=1,
                        expire_date=None
                    )
                    print("✅ Бот может создавать пригласительные ссылки")
                    print(f"🔗 Пример ссылки: {invite_link.invite_link}")
                    
                    return True
                    
                except TelegramError as e:
                    print(f"❌ Бот не может создавать пригласительные ссылки: {e}")
                    print("🔧 Нужно дать боту права на приглашение пользователей")
                    return False
                    
            else:
                print("❌ Бот НЕ является администратором канала")
                print("🔧 Нужно добавить бота как администратора с правами на приглашение")
                return False
                
        except TelegramError as e:
            print(f"❌ Ошибка при проверке прав бота: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def print_setup_instructions():
    """Печать инструкций по настройке"""
    print("\n" + "=" * 50)
    print("🔧 ИНСТРУКЦИИ ПО НАСТРОЙКЕ КАНАЛА")
    print("=" * 50)
    
    print("\n1️⃣ Откройте канал 'Аскеза✨ Верь в себя!':")
    print("   • Перейдите в канал")
    print("   • Нажмите на название канала")
    print("   • Выберите 'Управление каналом'")
    
    print("\n2️⃣ Добавьте бота как администратора:")
    print("   • Выберите 'Администраторы'")
    print("   • Нажмите 'Добавить администратора'")
    print("   • Найдите бота @Austerity_path_to_self_bot")
    print("   • Добавьте бота")
    
    print("\n3️⃣ Настройте права бота:")
    print("   • ✅ Приглашать пользователей")
    print("   • ✅ Добавлять участников")
    print("   • ✅ Удалять сообщения")
    print("   • ✅ Закреплять сообщения")
    
    print("\n4️⃣ Проверьте настройки:")
    print("   • Убедитесь, что бот имеет статус 'Администратор'")
    print("   • Проверьте, что у бота есть права на приглашение")
    print("   • Протестируйте создание пригласительной ссылки")
    
    print("\n5️⃣ После настройки:")
    print("   • Запустите бота: python run_no_webhook.py")
    print("   • Протестируйте кнопку 'Закрытый канал'")
    print("   • Проверьте, что пользователи получают приглашения")

async def test_channel_access_after_setup():
    """Тест доступа к каналу после настройки"""
    print("\n🧪 Тест доступа к каналу после настройки")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        await bot.initialize()
        
        # Тестируем создание пригласительной ссылки
        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                expire_date=None
            )
            print(f"✅ Пригласительная ссылка создана: {invite_link.invite_link}")
            
            # Тестируем отправку приглашения пользователю
            test_user_id = 760111270
            await bot.send_message(
                chat_id=test_user_id,
                text=f"📺 Добро пожаловать в закрытый канал Аскезы!\n\n{invite_link.invite_link}"
            )
            print(f"✅ Тестовое приглашение отправлено пользователю {test_user_id}")
            
            return True
            
        except TelegramError as e:
            print(f"❌ Ошибка при создании пригласительной ссылки: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

async def main():
    """Основная функция"""
    print("🔧 Исправление проблемы с доступом к каналу")
    print("=" * 50)
    
    # Проверяем текущее состояние
    access_ok = await check_and_fix_channel_access()
    
    if access_ok:
        print("\n✅ Доступ к каналу работает корректно!")
        print("Кнопка '📺 Закрытый канал' должна работать")
        
        # Тестируем после настройки
        test_ok = await test_channel_access_after_setup()
        
        if test_ok:
            print("\n🎉 Все работает! Пользователи будут получать приглашения в канал")
        else:
            print("\n⚠️ Есть проблемы с отправкой приглашений")
            print("Проверьте настройки бота и логи")
    else:
        print("\n❌ Проблемы с доступом к каналу!")
        print("Нужно настроить права бота")
        
        # Показываем инструкции
        print_setup_instructions()
    
    print("\n💡 Рекомендации:")
    print("1. Сделайте бота администратором канала")
    print("2. Дайте боту права на приглашение пользователей")
    print("3. Запустите бота: python run_no_webhook.py")
    print("4. Протестируйте кнопку 'Закрытый канал'")

if __name__ == "__main__":
    asyncio.run(main())
