#!/usr/bin/env python3
"""
Проверка ошибки доступа к каналу
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

async def check_bot_permissions():
    """Проверка прав бота в канале"""
    print("🔐 Проверка прав бота в канале")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        print(f"📺 Проверяем канал: {PRIVATE_CHANNEL_ID}")
        
        # Проверяем информацию о канале
        try:
            chat = await bot.get_chat(chat_id=PRIVATE_CHANNEL_ID)
            print(f"✅ Канал найден:")
            print(f"   • Название: {chat.title}")
            print(f"   • Тип: {chat.type}")
            print(f"   • Описание: {chat.description or 'Нет описания'}")
            print(f"   • Постоянная ссылка: {chat.invite_link or 'Нет постоянной ссылки'}")
            
        except TelegramError as e:
            print(f"❌ Ошибка при получении информации о канале: {e}")
            return False
        
        # Проверяем, является ли бот администратором
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
                    
                except TelegramError as e:
                    print(f"❌ Бот не может создавать пригласительные ссылки: {e}")
                    return False
                    
            else:
                print("❌ Бот НЕ является администратором канала")
                print("🔧 Нужно добавить бота как администратора с правами на приглашение")
                return False
                
        except TelegramError as e:
            print(f"❌ Ошибка при проверке прав бота: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

async def test_user_access(user_id: int):
    """Тест доступа пользователя к каналу"""
    print(f"\n👤 Тест доступа пользователя {user_id} к каналу")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Проверяем, есть ли пользователь в канале
        try:
            member = await bot.get_chat_member(
                chat_id=PRIVATE_CHANNEL_ID, 
                user_id=user_id
            )
            print(f"📺 Пользователь в канале: {member.status}")
            
            if member.status in ['member', 'administrator', 'creator']:
                print("✅ Пользователь уже в канале")
                return True
            else:
                print("❌ Пользователь не в канале")
                return False
                
        except TelegramError as e:
            if "user not found" in str(e).lower():
                print("❌ Пользователь не в канале")
                return False
            else:
                print(f"❌ Ошибка при проверке пользователя: {e}")
                return False
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании доступа: {e}")
        return False

async def test_adding_user_to_channel(user_id: int):
    """Тест добавления пользователя в канал"""
    print(f"\n➕ Тест добавления пользователя {user_id} в канал")
    print("=" * 50)
    
    try:
        bot = Bot(token=BOT_TOKEN)
        
        # Создаем пригласительную ссылку
        try:
            invite_link = await bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                expire_date=None
            )
            print(f"✅ Пригласительная ссылка создана: {invite_link.invite_link}")
            
            # Отправляем приглашение пользователю
            await bot.send_message(
                chat_id=user_id,
                text=f"📺 Добро пожаловать в закрытый канал Аскезы!\n\n{invite_link.invite_link}"
            )
            print(f"✅ Приглашение отправлено пользователю {user_id}")
            
            return True
            
        except TelegramError as e:
            print(f"❌ Ошибка при создании пригласительной ссылки: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        return False

def print_setup_instructions():
    """Печать инструкций по настройке"""
    print("\n" + "=" * 50)
    print("🔧 ИНСТРУКЦИИ ПО НАСТРОЙКЕ КАНАЛА")
    print("=" * 50)
    
    print("\n1️⃣ Настройте переменные окружения:")
    print("   • BOT_TOKEN - токен бота")
    print(f"   • PRIVATE_CHANNEL_ID={PRIVATE_CHANNEL_ID}")
    
    print("\n2️⃣ Добавьте бота в канал:")
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
    print("🔍 Проверка ошибки доступа к каналу")
    print("=" * 50)
    
    # Проверяем права бота
    bot_ok = await check_bot_permissions()
    
    if not bot_ok:
        print("\n❌ Проблемы с правами бота!")
        print_setup_instructions()
        return
    
    # Тестируем с пользователем 760111270
    user_id = 760111270
    
    # Проверяем доступ пользователя
    user_in_channel = await test_user_access(user_id)
    
    if not user_in_channel:
        print(f"\n🔄 Пользователь {user_id} не в канале, пытаемся добавить...")
        
        # Пытаемся добавить пользователя
        success = await test_adding_user_to_channel(user_id)
        
        if success:
            print(f"✅ Пользователь {user_id} добавлен в канал")
        else:
            print(f"❌ Не удалось добавить пользователя {user_id} в канал")
    else:
        print(f"✅ Пользователь {user_id} уже в канале")
    
    print("\n💡 Рекомендации:")
    print("1. Убедитесь, что бот является администратором канала")
    print("2. Проверьте, что у бота есть права на приглашение")
    print("3. Запустите бота: python run_no_webhook.py")
    print("4. Протестируйте кнопку 'Закрытый канал'")

if __name__ == "__main__":
    asyncio.run(main())
