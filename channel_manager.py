import logging
from telegram import Bot, ChatMember
from telegram.error import TelegramError
from config import BOT_TOKEN, PRIVATE_CHANNEL_ID
from database import Database

logger = logging.getLogger(__name__)

class ChannelManager:
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.db = Database()
    
    async def check_bot_permissions(self) -> dict:
        """Проверка прав бота в каналах и чатах"""
        permissions = {
            'channel': {'is_admin': False, 'can_invite': False, 'error': None},
            'chat': {'is_admin': False, 'can_invite': False, 'error': None}
        }
        
        # Инициализируем бота если нужно
        if not self.bot._initialized:
            await self.bot.initialize()
        
        # Проверяем права в канале
        if PRIVATE_CHANNEL_ID:
            try:
                bot_member = await self.bot.get_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=self.bot.id)
                permissions['channel']['is_admin'] = bot_member.status in ['administrator', 'creator']
                
                if permissions['channel']['is_admin']:
                    # Проверяем права на приглашение
                    try:
                        await self.bot.create_chat_invite_link(chat_id=PRIVATE_CHANNEL_ID, member_limit=1)
                        permissions['channel']['can_invite'] = True
                    except TelegramError as e:
                        permissions['channel']['error'] = str(e)
            except TelegramError as e:
                permissions['channel']['error'] = str(e)
        
        # Проверяем права в чате (если настроен)
        try:
            from config import PRIVATE_CHAT_ID
            if PRIVATE_CHAT_ID:
                try:
                    bot_member = await self.bot.get_chat_member(chat_id=PRIVATE_CHAT_ID, user_id=self.bot.id)
                    permissions['chat']['is_admin'] = bot_member.status in ['administrator', 'creator']
                    
                    if permissions['chat']['is_admin']:
                        # Проверяем права на приглашение
                        try:
                            await self.bot.create_chat_invite_link(chat_id=PRIVATE_CHAT_ID, member_limit=1)
                            permissions['chat']['can_invite'] = True
                        except TelegramError as e:
                            permissions['chat']['error'] = str(e)
                except TelegramError as e:
                    permissions['chat']['error'] = str(e)
        except ImportError:
            # PRIVATE_CHAT_ID не настроен
            permissions['chat']['error'] = 'PRIVATE_CHAT_ID не настроен'
        
        return permissions
    
    async def add_user_to_channel(self, user_id: int) -> bool:
        """Добавление пользователя в закрытый канал"""
        if not PRIVATE_CHANNEL_ID:
            logger.warning("PRIVATE_CHANNEL_ID не настроен")
            return False
        
        try:
            # Инициализируем бота если нужно
            if not self.bot._initialized:
                await self.bot.initialize()
            
            # Проверяем, является ли бот администратором канала
            bot_member = await self.bot.get_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=self.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                logger.error(f"Бот не является администратором канала {PRIVATE_CHANNEL_ID}")
                return False
            
            # Проверяем, есть ли у бота права на приглашение пользователей
            chat = await self.bot.get_chat(chat_id=PRIVATE_CHANNEL_ID)
            if not chat.invite_link:
                logger.warning("У канала нет постоянной пригласительной ссылки")
            
            # Создаем временную пригласительную ссылку
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                expire_date=None  # Ссылка не истекает
            )
            
            # Отправляем приглашение пользователю
            await self.bot.send_message(
                chat_id=user_id,
                text=f"📺 Добро пожаловать в закрытый канал Аскезы!\n\n{invite_link.invite_link}"
            )
            
            logger.info(f"Пользователь {user_id} добавлен в канал")
            return True
            
        except TelegramError as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id} в канал: {e}")
            if "Not enough rights" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                logger.error("Бот не имеет достаточных прав для добавления пользователей в канал")
            return False
    
    async def add_user_to_chat(self, user_id: int) -> bool:
        """Добавление пользователя в закрытый чат"""
        try:
            from config import PRIVATE_CHAT_ID
            if not PRIVATE_CHAT_ID:
                logger.warning("PRIVATE_CHAT_ID не настроен")
                return False
        except ImportError:
            logger.warning("PRIVATE_CHAT_ID не настроен")
            return False
        
        try:
            # Инициализируем бота если нужно
            if not self.bot._initialized:
                await self.bot.initialize()
            
            # Получаем PRIVATE_CHAT_ID
            from config import PRIVATE_CHAT_ID
            
            # Проверяем, является ли бот администратором чата
            bot_member = await self.bot.get_chat_member(chat_id=PRIVATE_CHAT_ID, user_id=self.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                logger.error(f"Бот не является администратором чата {PRIVATE_CHAT_ID}")
                return False
            
            # Проверяем, есть ли у бота права на приглашение пользователей
            chat = await self.bot.get_chat(chat_id=PRIVATE_CHAT_ID)
            if not chat.invite_link:
                logger.warning("У чата нет постоянной пригласительной ссылки")
            
            # Создаем временную пригласительную ссылку
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHAT_ID,
                member_limit=1,
                expire_date=None  # Ссылка не истекает
            )
            
            # Отправляем приглашение пользователю
            await self.bot.send_message(
                chat_id=user_id,
                text=f"💬 Добро пожаловать в закрытый чат Аскезы!\n\n{invite_link.invite_link}"
            )
            
            logger.info(f"Пользователь {user_id} добавлен в чат")
            return True
            
        except TelegramError as e:
            logger.error(f"Ошибка при добавлении пользователя {user_id} в чат: {e}")
            if "Not enough rights" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                logger.error("Бот не имеет достаточных прав для добавления пользователей в чат")
            return False
    
    async def remove_user_from_channel(self, user_id: int) -> bool:
        """Удаление пользователя из закрытого канала"""
        if not PRIVATE_CHANNEL_ID:
            logger.warning("PRIVATE_CHANNEL_ID не настроен")
            return False
        
        try:
            # Инициализируем бота если нужно
            if not self.bot._initialized:
                await self.bot.initialize()
            
            # Проверяем, является ли бот администратором канала
            bot_member = await self.bot.get_chat_member(PRIVATE_CHANNEL_ID, self.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                logger.error("Бот не является администратором канала")
                return False
            
            # Удаляем пользователя из канала
            await self.bot.ban_chat_member(PRIVATE_CHANNEL_ID, user_id)
            
            logger.info(f"Пользователь {user_id} удален из канала")
            return True
            
        except TelegramError as e:
            logger.error(f"Ошибка при удалении пользователя {user_id} из канала: {e}")
            return False
    
    async def remove_user_from_chat(self, user_id: int) -> bool:
        """Удаление пользователя из закрытого чата"""
        try:
            from config import PRIVATE_CHAT_ID
            if not PRIVATE_CHAT_ID:
                logger.warning("PRIVATE_CHAT_ID не настроен")
                return False
        except ImportError:
            logger.warning("PRIVATE_CHAT_ID не настроен")
            return False
        
        try:
            # Инициализируем бота если нужно
            if not self.bot._initialized:
                await self.bot.initialize()
            
            # Получаем PRIVATE_CHAT_ID
            from config import PRIVATE_CHAT_ID
            
            # Проверяем, является ли бот администратором чата
            bot_member = await self.bot.get_chat_member(PRIVATE_CHAT_ID, self.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                logger.error("Бот не является администратором чата")
                return False
            
            # Удаляем пользователя из чата
            await self.bot.ban_chat_member(PRIVATE_CHAT_ID, user_id)
            
            logger.info(f"Пользователь {user_id} удален из чата")
            return True
            
        except TelegramError as e:
            logger.error(f"Ошибка при удалении пользователя {user_id} из чата: {e}")
            return False
    
    async def check_user_in_channel(self, user_id: int) -> bool:
        """Проверка, находится ли пользователь в канале"""
        if not PRIVATE_CHANNEL_ID:
            return False
        
        try:
            member = await self.bot.get_chat_member(PRIVATE_CHANNEL_ID, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except TelegramError:
            return False
    
    async def send_channel_invite(self, user_id: int) -> bool:
        """Отправка пригласительной ссылки на канал пользователю"""
        if not PRIVATE_CHANNEL_ID:
            logger.warning("PRIVATE_CHANNEL_ID не настроен")
            return False
        
        try:
            # Инициализируем бота если нужно
            if not self.bot._initialized:
                await self.bot.initialize()
            
            # Проверяем, является ли бот администратором канала
            bot_member = await self.bot.get_chat_member(chat_id=PRIVATE_CHANNEL_ID, user_id=self.bot.id)
            if bot_member.status not in ['administrator', 'creator']:
                logger.error(f"Бот не является администратором канала {PRIVATE_CHANNEL_ID}")
                return False
            
            # Получаем информацию о канале
            chat = await self.bot.get_chat(chat_id=PRIVATE_CHANNEL_ID)
            channel_name = chat.title or "Закрытый канал Аскезы"
            
            # Создаем пригласительную ссылку
            invite_link = await self.bot.create_chat_invite_link(
                chat_id=PRIVATE_CHANNEL_ID,
                member_limit=1,
                expire_date=None
            )
            
            # Отправляем приглашение пользователю
            invite_text = f"""
📺 {channel_name}

Для получения доступа к эксклюзивному контенту подпишитесь на наш закрытый канал:

{invite_link.invite_link}

После подписки нажмите кнопку "Проверить подписку" для подтверждения.
            """
            
            await self.bot.send_message(
                chat_id=user_id,
                text=invite_text
            )
            
            logger.info(f"Пригласительная ссылка отправлена пользователю {user_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Ошибка при отправке пригласительной ссылки пользователю {user_id}: {e}")
            return False
    
    async def check_user_in_chat(self, user_id: int) -> bool:
        """Проверка, находится ли пользователь в чате"""
        try:
            from config import PRIVATE_CHAT_ID
            if not PRIVATE_CHAT_ID:
                return False
        except ImportError:
            return False
        
        try:
            member = await self.bot.get_chat_member(PRIVATE_CHAT_ID, user_id)
            return member.status in ['member', 'administrator', 'creator']
        except TelegramError:
            return False
    
    async def grant_access_to_user(self, user_id: int, access_type: str) -> bool:
        """Предоставление доступа пользователю"""
        success = True
        
        # Добавляем в базу данных
        if not self.db.grant_access(user_id, access_type):
            success = False
        
        # Добавляем в канал и чат
        if not await self.add_user_to_channel(user_id):
            success = False
        
        if not await self.add_user_to_chat(user_id):
            success = False
        
        return success
    
    async def revoke_access_from_user(self, user_id: int) -> bool:
        """Отзыв доступа у пользователя"""
        success = True
        
        # Удаляем из канала и чата
        if not await self.remove_user_from_channel(user_id):
            success = False
        
        if not await self.remove_user_from_chat(user_id):
            success = False
        
        return success
