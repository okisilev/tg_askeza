#!/usr/bin/env python3
"""
Тест доступа к каналу и создания пригласительных ссылок
"""

import asyncio
import logging
from telegram import Bot
from config import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_channel_access():
    """Тестирует доступ к каналу и создание пригласительных ссылок"""
    
    print("🔍 Тестирование доступа к каналу...")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print(f"🤖 Токен бота: {config.BOT_TOKEN[:20]}...")
    
    try:
        # Создаем бота
        bot = Bot(token=config.BOT_TOKEN)
        
        # Инициализируем бота
        await bot.initialize()
        print("✅ Бот инициализирован")
        
        # Проверяем информацию о канале
        try:
            chat_info = await bot.get_chat(chat_id=int(config.PRIVATE_CHANNEL_ID))
            print(f"✅ Информация о канале получена:")
            print(f"   📝 Название: {chat_info.title}")
            print(f"   🆔 ID: {chat_info.id}")
            print(f"   📱 Тип: {chat_info.type}")
        except Exception as e:
            print(f"❌ Ошибка при получении информации о канале: {e}")
            return
        
        # Проверяем права бота в канале
        try:
            bot_member = await bot.get_chat_member(
                chat_id=int(config.PRIVATE_CHANNEL_ID),
                user_id=bot.id
            )
            print(f"✅ Статус бота в канале: {bot_member.status}")
            
            if bot_member.status == "administrator":
                print("✅ Бот является администратором")
                
                # Проверяем права администратора
                if hasattr(bot_member, 'can_invite_users') and bot_member.can_invite_users:
                    print("✅ Бот может приглашать пользователей")
                else:
                    print("❌ Бот НЕ может приглашать пользователей")
                    
                if hasattr(bot_member, 'can_manage_chat') and bot_member.can_manage_chat:
                    print("✅ Бот может управлять чатом")
                else:
                    print("❌ Бот НЕ может управлять чатом")
            else:
                print(f"❌ Бот НЕ является администратором. Статус: {bot_member.status}")
                return
                
        except Exception as e:
            print(f"❌ Ошибка при проверке прав бота: {e}")
            return
        
        # Пытаемся создать пригласительную ссылку
        try:
            print("🔗 Создаем пригласительную ссылку...")
            invite_link = await bot.create_chat_invite_link(
                chat_id=int(config.PRIVATE_CHANNEL_ID),
                member_limit=1,
                expire_date=None
            )
            print(f"✅ Пригласительная ссылка создана:")
            print(f"   🔗 Ссылка: {invite_link.invite_link}")
            print(f"   👥 Лимит участников: {invite_link.member_limit}")
            print(f"   ⏰ Истекает: {invite_link.expire_date or 'Никогда'}")
            
        except Exception as e:
            print(f"❌ Ошибка при создании пригласительной ссылки: {e}")
            return
        
        # Пытаемся получить существующие ссылки
        try:
            print("🔗 Получаем существующие пригласительные ссылки...")
            invite_links = await bot.get_chat_administrators(chat_id=int(config.PRIVATE_CHANNEL_ID))
            print(f"✅ Администраторы канала получены: {len(invite_links)}")
            
        except Exception as e:
            print(f"❌ Ошибка при получении администраторов: {e}")
        
        print("✅ Тест завершен успешно!")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")
        logger.error(f"Общая ошибка: {e}")
    finally:
        # Закрываем бота
        try:
            await bot.shutdown()
            print("✅ Бот закрыт")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(test_channel_access())
