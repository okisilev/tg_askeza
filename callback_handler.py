#!/usr/bin/env python3
"""
Обработчик callback'ов для инлайн кнопок
"""

import logging
import asyncio
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from database import Database
from channel_manager import ChannelManager
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

logger = logging.getLogger(__name__)

class CallbackHandler:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.db = Database()
        self.channel_manager = ChannelManager()
    
    async def handle_callback(self, callback_data: str, user_id: int):
        """Обработка callback'ов от инлайн кнопок"""
        try:
            logger.info(f"Обрабатываем callback: {callback_data} для пользователя {user_id}")
            
            if callback_data == "private_channel":
                await self.give_channel_access(user_id)
            elif callback_data == "private_chat":
                await self.give_chat_access(user_id)
            elif callback_data == "back_to_main":
                await self.show_main_menu(user_id)
            else:
                logger.warning(f"Неизвестный callback: {callback_data}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке callback {callback_data}: {e}")
    
    async def give_channel_access(self, user_id: int):
        """Предоставление доступа к каналу"""
        try:
            # Проверяем, есть ли у пользователя доступ
            user_access = self.db.get_user_access(user_id)
            if not user_access:
                await self.bot.send_message(
                    chat_id=user_id,
                    text="❌ У вас нет активного доступа. Сначала оплатите подписку."
                )
                return
            
            if PRIVATE_CHANNEL_ID:
                channel_text = f"""
📺 Закрытый канал Аскезы

Присоединяйтесь к нашему закрытому каналу для получения эксклюзивных материалов:
https://t.me/{PRIVATE_CHANNEL_ID.replace('@', '')}
                """
            else:
                channel_text = "❌ Канал не настроен. Обратитесь к администратору."
            
            await self.bot.send_message(chat_id=user_id, text=channel_text)
            logger.info(f"Доступ к каналу предоставлен пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при предоставлении доступа к каналу: {e}")
            await self.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при предоставлении доступа к каналу."
            )
    
    async def give_chat_access(self, user_id: int):
        """Предоставление доступа к чату"""
        try:
            # Проверяем, есть ли у пользователя доступ
            user_access = self.db.get_user_access(user_id)
            if not user_access:
                await self.bot.send_message(
                    chat_id=user_id,
                    text="❌ У вас нет активного доступа. Сначала оплатите подписку."
                )
                return
            
            if PRIVATE_CHAT_ID:
                chat_text = f"""
💬 Закрытый чат Аскезы

Присоединяйтесь к нашему закрытому чату для общения с единомышленниками:
https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}
                """
            else:
                chat_text = "❌ Чат не настроен. Обратитесь к администратору."
            
            await self.bot.send_message(chat_id=user_id, text=chat_text)
            logger.info(f"Доступ к чату предоставлен пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при предоставлении доступа к чату: {e}")
            await self.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при предоставлении доступа к чату."
            )
    
    async def show_main_menu(self, user_id: int):
        """Показ главного меню"""
        try:
            user_access = self.db.get_user_access(user_id)
            has_access = len(user_access) > 0
            
            if has_access:
                keyboard = [
                    [InlineKeyboardButton("❓ Вопрос/Ответ", callback_data="faq")],
                    [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                    [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                    [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")]
                ]
            else:
                keyboard = [
                    [InlineKeyboardButton("❓ Вопрос/Ответ", callback_data="faq")],
                    [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            main_text = """
🌟 Добро пожаловать в бот Аскезы! 🌟

Выберите, что вас интересует:
            """
            
            await self.bot.send_message(
                chat_id=user_id,
                text=main_text,
                reply_markup=reply_markup
            )
            logger.info(f"Главное меню показано пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при показе главного меню: {e}")
            await self.bot.send_message(
                chat_id=user_id,
                text="❌ Произошла ошибка при загрузке меню."
            )

# Создаем глобальный экземпляр обработчика
callback_handler = CallbackHandler()
