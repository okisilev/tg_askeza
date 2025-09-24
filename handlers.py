import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from database import Database
from yookassa_client import YooKassaClient
from channel_manager import ChannelManager
from config import PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self):
        self.db = Database()
        self.yookassa = YooKassaClient()
        self.channel_manager = ChannelManager()
    
    def get_channel_url(self):
        """Получение правильной ссылки на канал"""
        if not PRIVATE_CHANNEL_ID:
            return None
        
        if PRIVATE_CHANNEL_ID.startswith('@'):
            # Для каналов с @username
            return f"https://t.me/{PRIVATE_CHANNEL_ID.replace('@', '')}"
        else:
            # Для числовых ID каналов (например, -1002806695160)
            # Убираем -100 и используем оставшуюся часть
            channel_id = PRIVATE_CHANNEL_ID[4:] if PRIVATE_CHANNEL_ID.startswith('-100') else PRIVATE_CHANNEL_ID
            return f"https://t.me/c/{channel_id}"
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        logger.info(f"Получена команда /start от пользователя {user.id}")
        
        # Добавляем пользователя в базу данных
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Приветственное сообщение
        welcome_text = """
🌟 Добро пожаловать в бот Аскезы! 🌟

Аскеза — это древняя практика духовного развития, которая помогает:
• Развить силу воли и самодисциплину
• Очистить разум от негативных мыслей
• Улучшить концентрацию и фокус
• Достичь внутренней гармонии и баланса

Выберите, что вас интересует:
        """
        
        keyboard = [
            [KeyboardButton("❓ Вопрос/Ответ"), KeyboardButton("💳 Оплатить доступ")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text
        user_id = update.effective_user.id
        
        logger.info(f"Получено сообщение: '{text}' от пользователя {user_id}")
        
        if text == "❓ Вопрос/Ответ":
            await self.show_faq_text(update)
        elif text == "💳 Оплатить доступ":
            await self.show_payment_options_text(update)
        elif text == "🔙 Назад":
            await self.show_main_menu_text(update)
        elif text == "📺 Закрытый канал":
            await self.give_channel_access_text(update)
        elif text == "💬 Закрытый чат":
            await self.give_chat_access_text(update)
        elif text == "🔸 Аскеза - 990₽":
            await self.create_payment_text(update, "askeza")
        elif text == "🔸 Нумерология - 2490₽":
            await self.create_payment_text(update, "numerology")
        elif text == "📋 Проверить платежи":
            await self.show_payment_history_text(update)
        else:
            await update.message.reply_text("Используйте кнопки для навигации.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик нажатий на кнопки"""
        logger.info("=== НАЧАЛО ОБРАБОТКИ КНОПКИ ===")
        try:
            query = update.callback_query
            logger.info(f"Query получен: {query}")
            await query.answer()
            
            data = query.data
            user_id = query.from_user.id
            
            logger.info(f"Получен callback: {data} от пользователя {user_id}")
            
            if data == "faq":
                logger.info("Переходим к FAQ")
                await self.show_faq(query)
            elif data == "payment":
                logger.info("Переходим к оплате")
                await self.show_payment_options(query)
            elif data == "back_to_main":
                await self.show_main_menu(query)
            elif data.startswith("pay_"):
                payment_type = data.split("_")[1]
                logger.info(f"Создаем платеж для типа: {payment_type}")
                logger.info(f"Callback data: {data}")
                await self.create_payment(query, payment_type)
            elif data == "check_access":
                await self.show_access_status(query)
            elif data == "check_payments":
                await self.show_payment_history(query)
            elif data == "private_channel":
                await self.give_channel_access(query)
            elif data == "private_chat":
                await self.give_chat_access(query)
            elif data == "check_subscription":
                await self.check_subscription(query)
            else:
                logger.warning(f"Неизвестный callback: {data}")
        except Exception as e:
            logger.error(f"Ошибка в button_callback: {e}")
            if update.callback_query:
                await update.callback_query.answer("Произошла ошибка. Попробуйте позже.")
    
    async def show_faq(self, query):
        """Показ часто задаваемых вопросов"""
        faq_text = """
❓ Часто задаваемые вопросы:

🔸 Что такое Аскеза?
Аскеза — это духовная практика, направленная на развитие силы воли через добровольные ограничения и самодисциплину.

🔸 Сколько длится курс?
Доступ к материалам Аскезы предоставляется на 30 дней с момента оплаты.

🔸 Что включает в себя нумерологический разбор?
Персональный анализ вашей даты рождения, имени и жизненного пути с рекомендациями по развитию.

🔸 Как происходит оплата?
Оплата происходит через безопасную систему ЮKassa. Поддерживаются все основные способы оплаты.

🔸 Когда я получу доступ?
Доступ предоставляется автоматически сразу после успешной оплаты.

🔸 Можно ли продлить доступ?
Да, вы можете продлить доступ в любое время через бота.
        """
        
        keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(faq_text, reply_markup=reply_markup)
    
    async def show_faq_text(self, update):
        """Показ FAQ для текстовых сообщений"""
        faq_text = """
❓ Часто задаваемые вопросы:

🔸 Что такое Аскеза?
Аскеза — это духовная практика, направленная на развитие силы воли через добровольные ограничения и самодисциплину.

🔸 Сколько длится курс?
Доступ к материалам Аскезы предоставляется на 30 дней с момента оплаты.

🔸 Что включает в себя нумерологический разбор?
Персональный анализ вашей даты рождения, имени и жизненного пути с рекомендациями по развитию.

🔸 Как происходит оплата?
Оплата происходит через безопасную систему ЮKassa. Поддерживаются все основные способы оплаты.

🔸 Когда я получу доступ?
Доступ предоставляется автоматически сразу после успешной оплаты.

🔸 Можно ли продлить доступ?
Да, вы можете продлить доступ в любое время через бота.
        """
        
        keyboard = [[KeyboardButton("🔙 Назад")]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(faq_text, reply_markup=reply_markup)
    
    async def show_payment_options_text(self, update):
        """Показ вариантов оплаты для текстовых сообщений"""
        payment_text = """
💳 Выберите тип доступа:

🔸 Аскеза - 990₽
Доступ к закрытому каналу с материалами по Аскезе на 30 дней

🔸 Нумерология - 2490₽
Персональный анализ и рекомендации от эксперта
        """
        
        keyboard = [
            [KeyboardButton("🔸 Аскеза - 990₽"), KeyboardButton("🔸 Нумерология - 2490₽")],
            [KeyboardButton("📋 Проверить платежи")],
            [KeyboardButton("🔙 Назад")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        await update.message.reply_text(payment_text, reply_markup=reply_markup)
    
    async def show_main_menu_text(self, update):
        """Показ главного меню для текстовых сообщений"""
        user_id = update.effective_user.id
        user_access = self.db.get_user_access(user_id)
        
        # Проверяем, есть ли у пользователя активный доступ
        has_access = len(user_access) > 0
        
        if has_access:
            # Показываем кнопки доступа
            keyboard = [
                [KeyboardButton("❓ Вопрос/Ответ")],
                [KeyboardButton("📺 Закрытый канал"), KeyboardButton("💬 Закрытый чат")],
                [KeyboardButton("💳 Оплатить доступ")]
            ]
        else:
            # Обычное меню
            keyboard = [
                [KeyboardButton("❓ Вопрос/Ответ"), KeyboardButton("💳 Оплатить доступ")]
            ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        main_text = """
🌟 Добро пожаловать в бот Аскезы! 🌟
Аскеза — это древняя практика духовного развития, которая помогает:
• Развить силу воли и самодисциплину
• Очистить разум от негативных мыслей
• Улучшить концентрацию и фокус
• Достичь внутренней гармонии и баланса
Выберите, что вас интересует:
        """
        
        await update.message.reply_text(main_text, reply_markup=reply_markup)
    
    async def show_payment_options(self, query):
        """Показ вариантов оплаты"""
        try:
            logger.info("Показываем варианты оплаты")
            payment_text = """
💳 Выберите тип доступа:

🔸 Аскеза - 990₽
Доступ к закрытому каналу с материалами по Аскезе на 30 дней

🔸 Нумерология - 2490₽
Персональный анализ и рекомендации от эксперта
        """
            
            keyboard = [
                [InlineKeyboardButton("🔸 Аскеза - 990₽", callback_data="pay_askeza")],
                [InlineKeyboardButton("🔸 Нумерология - 2490₽", callback_data="pay_numerology")],
                [InlineKeyboardButton("📋 Проверить платежи", callback_data="check_payments")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(payment_text, reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Ошибка в show_payment_options: {e}")
            await query.edit_message_text("Произошла ошибка при загрузке вариантов оплаты.")
    
    async def show_main_menu(self, query):
        """Показ главного меню"""
        user_id = query.from_user.id
        user_access = self.db.get_user_access(user_id)
        
        # Проверяем, есть ли у пользователя активный доступ
        has_access = len(user_access) > 0
        
        if has_access:
            # Показываем кнопки доступа
            keyboard = [
                [InlineKeyboardButton("❓ Вопрос/Ответ", callback_data="faq")],
                [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")]
            ]
        else:
            # Обычное меню
            keyboard = [
                [InlineKeyboardButton("❓ Вопрос/Ответ", callback_data="faq")],
                [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        main_text = """
🌟 Добро пожаловать в бот Аскезы! 🌟

Выберите, что вас интересует:
        """
        
        await query.edit_message_text(main_text, reply_markup=reply_markup)
    
    async def create_payment(self, query, payment_type: str):
        """Создание платежа"""
        user_id = query.from_user.id
        
        logger.info(f"Создание платежа: тип={payment_type}, пользователь={user_id}")
        
        try:
            amount = self.yookassa.get_payment_amount(payment_type)
            description = self.yookassa.get_payment_description(payment_type)
            
            logger.info(f"Сумма: {amount}, описание: {description}")
            
            # Создаем платеж в ЮKassa
            payment_result = self.yookassa.create_payment(
                amount=amount,
                description=description,
                return_url=f"https://t.me/your_bot"
            )
            
            if payment_result["success"]:
                # Сохраняем платеж в базу данных
                self.db.create_payment(
                    user_id=user_id,
                    payment_type=payment_type,
                    amount=amount,
                    yookassa_payment_id=payment_result["payment_id"]
                )
                
                payment_text = f"""
💳 Оплата {description}

💰 Сумма: {amount}₽
🆔 ID платежа: {payment_result["payment_id"]}

Нажмите на кнопку ниже для перехода к оплате:
                """
                
                keyboard = [
                    [InlineKeyboardButton("💳 Оплатить", url=payment_result["confirmation_url"])],
                    [InlineKeyboardButton("🔍 Проверить статус", callback_data="check_access")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="payment")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(payment_text, reply_markup=reply_markup)
            else:
                error_text = f"❌ Ошибка при создании платежа: {payment_result.get('error', 'Неизвестная ошибка')}"
                keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="payment")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(error_text, reply_markup=reply_markup)
                
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            error_text = "❌ Произошла ошибка при создании платежа. Попробуйте позже."
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="payment")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_text, reply_markup=reply_markup)
    
    async def show_access_status(self, query):
        """Показ статуса доступа"""
        user_id = query.from_user.id
        user_access = self.db.get_user_access(user_id)
        
        if user_access:
            access_text = "✅ У вас есть активный доступ:\n\n"
            for access in user_access:
                access_type = "Аскеза" if access["access_type"] == "askeza" else "Нумерологический разбор"
                expires_at = access["expires_at"]
                access_text += f"🔸 {access_type} - до {expires_at}\n"
            
            keyboard = [
                [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        else:
            access_text = "❌ У вас нет активного доступа. Оплатите подписку для получения доступа к материалам."
            keyboard = [
                [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(access_text, reply_markup=reply_markup)
    
    async def show_payment_history(self, query):
        """Показ истории платежей и проверка их статуса"""
        user_id = query.from_user.id
        
        try:
            logger.info(f"Показываем историю платежей для пользователя {user_id}")
            
            # Получаем все платежи пользователя
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT yookassa_payment_id, payment_type, amount, status, created_at, paid_at
                    FROM payments 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 10
                ''', (user_id,))
                payments = cursor.fetchall()
            
            if not payments:
                history_text = """
📋 История платежей

У вас пока нет платежей.
                """
                keyboard = [
                    [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
            else:
                history_text = "📋 История платежей:\n\n"
                updated_payments = []
                
                for payment in payments:
                    payment_id = payment['yookassa_payment_id']
                    payment_type = payment['payment_type']
                    amount = payment['amount']
                    status = payment['status']
                    created_at = payment['created_at']
                    paid_at = payment['paid_at']
                    
                    # Проверяем статус в ЮKassa для pending платежей
                    if status == 'pending':
                        try:
                            status_result = self.yookassa.get_payment_status(payment_id)
                            if status_result["success"]:
                                new_status = status_result["status"]
                                if new_status != status:
                                    # Обновляем статус в БД
                                    self.db.update_payment_status(payment_id, new_status)
                                    status = new_status
                                    logger.info(f"Статус платежа {payment_id} обновлен: {status}")
                        except Exception as e:
                            logger.error(f"Ошибка при проверке статуса платежа {payment_id}: {e}")
                    
                    # Форматируем тип платежа
                    type_name = "Аскеза" if payment_type == "askeza" else "Нумерологический разбор"
                    
                    # Форматируем статус
                    status_emoji = {
                        'pending': '⏳',
                        'succeeded': '✅',
                        'canceled': '❌'
                    }.get(status, '❓')
                    
                    # Форматируем дату
                    from datetime import datetime
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
                    except:
                        created_date = created_at
                    
                    history_text += f"{status_emoji} {type_name} - {amount}₽\n"
                    history_text += f"   ID: {payment_id[:8]}...\n"
                    history_text += f"   Дата: {created_date}\n"
                    if paid_at:
                        try:
                            paid_date = datetime.fromisoformat(paid_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
                            history_text += f"   Оплачен: {paid_date}\n"
                        except:
                            pass
                    history_text += "\n"
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Обновить статусы", callback_data="check_payments")],
                    [InlineKeyboardButton("💳 Оплатить доступ", callback_data="payment")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(history_text, reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Ошибка при показе истории платежей: {e}")
            error_text = "❌ Произошла ошибка при загрузке истории платежей."
            keyboard = [
                [InlineKeyboardButton("🔙 Назад", callback_data="payment")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(error_text, reply_markup=reply_markup)
    
    async def give_channel_access(self, query):
        """Предоставление доступа к каналу"""
        user_id = query.from_user.id
        
        # Проверяем, есть ли у пользователя доступ
        user_access = self.db.get_user_access(user_id)
        if not user_access:
            await query.edit_message_text("❌ У вас нет активного доступа. Сначала оплатите подписку.")
            return
        
        if not PRIVATE_CHANNEL_ID:
            await query.edit_message_text("❌ Канал не настроен. Обратитесь к администратору.")
            return
        
        # Проверяем, находится ли пользователь уже в канале
        in_channel = await self.channel_manager.check_user_in_channel(user_id)
        
        if in_channel:
            # Пользователь уже в канале - показываем кнопку для перехода
            channel_text = """
📺 Закрытый канал Аскезы

✅ Вы уже состоите в нашем закрытом канале!
Нажмите кнопку ниже для перехода в канал.
            """
            channel_url = self.get_channel_url()
            keyboard = [
                [InlineKeyboardButton("📺 Перейти в канал", url=channel_url)],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        else:
            # Пользователь не в канале - добавляем его автоматически
            success = await self.channel_manager.add_user_to_channel(user_id)
            if success:
                channel_text = """
📺 Закрытый канал Аскезы

✅ Вы были добавлены в закрытый канал!
Нажмите кнопку ниже для перехода в канал.
                """
                channel_url = self.get_channel_url()
                keyboard = [
                    [InlineKeyboardButton("📺 Перейти в канал", url=channel_url)],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
            else:
                channel_text = """
📺 Закрытый канал Аскезы

❌ Произошла ошибка при добавлении в канал.

Возможные причины:
• Бот не является администратором канала
• У бота нет прав на приглашение пользователей
• Канал не настроен в системе

Обратитесь к администратору для решения проблемы.
                """
                keyboard = [
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(channel_text, reply_markup=reply_markup)
    
    async def check_subscription(self, query):
        """Проверка подписки на канал"""
        user_id = query.from_user.id
        
        # Проверяем, есть ли у пользователя доступ
        user_access = self.db.get_user_access(user_id)
        if not user_access:
            await query.edit_message_text("❌ У вас нет активного доступа. Сначала оплатите подписку.")
            return
        
        if not PRIVATE_CHANNEL_ID:
            await query.edit_message_text("❌ Канал не настроен. Обратитесь к администратору.")
            return
        
        # Проверяем подписку на канал
        in_channel = await self.channel_manager.check_user_in_channel(user_id)
        
        if in_channel:
            # Пользователь подписан - даем доступ к каналу
            channel_text = """
📺 Закрытый канал Аскезы

✅ Отлично! Вы подписаны на наш канал!
Теперь у вас есть доступ к эксклюзивному контенту.

Нажмите кнопку ниже для перехода в канал.
            """
            channel_url = self.get_channel_url()
            keyboard = [
                [InlineKeyboardButton("📺 Перейти в канал", url=channel_url)],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        else:
            # Пользователь не подписан
            channel_text = """
📺 Закрытый канал Аскезы

❌ Вы еще не подписаны на канал.

Пожалуйста, подпишитесь на канал по ссылке, которая была отправлена вам ранее, и попробуйте снова.
            """
            keyboard = [
                [InlineKeyboardButton("🔄 Проверить снова", callback_data="check_subscription")],
                [InlineKeyboardButton("📺 Получить ссылку", callback_data="private_channel")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(channel_text, reply_markup=reply_markup)
    
    async def give_chat_access(self, query):
        """Предоставление доступа к чату"""
        user_id = query.from_user.id
        
        # Проверяем, есть ли у пользователя доступ
        user_access = self.db.get_user_access(user_id)
        if not user_access:
            await query.edit_message_text("❌ У вас нет активного доступа. Сначала оплатите подписку.")
            return
        
        if not PRIVATE_CHAT_ID:
            await query.edit_message_text("❌ Чат не настроен. Обратитесь к администратору.")
            return
        
        # Проверяем, находится ли пользователь уже в чате
        in_chat = await self.channel_manager.check_user_in_chat(user_id)
        
        if in_chat:
            # Пользователь уже в чате - показываем кнопку для перехода
            chat_text = """
💬 Закрытый чат Аскезы

Вы уже состоите в нашем закрытом чате!
Нажмите кнопку ниже для перехода в чат.
            """
            keyboard = [
                [InlineKeyboardButton("💬 Перейти в чат", url=f"https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
            ]
        else:
            # Добавляем пользователя в чат
            success = await self.channel_manager.add_user_to_chat(user_id)
            if success:
                chat_text = """
💬 Закрытый чат Аскезы

Вы были добавлены в закрытый чат!
Нажмите кнопку ниже для перехода в чат.
                """
                keyboard = [
                    [InlineKeyboardButton("💬 Перейти в чат", url=f"https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
            else:
                chat_text = """
💬 Закрытый чат Аскезы

❌ Произошла ошибка при добавлении в чат.

Возможные причины:
• Бот не является администратором чата
• У бота нет прав на приглашение пользователей
• Чат не настроен в системе

Обратитесь к администратору для решения проблемы.
                """
                keyboard = [
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
                ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(chat_text, reply_markup=reply_markup)
    
    async def process_payment_webhook(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка webhook от ЮKassa"""
        try:
            # Получаем данные из webhook
            webhook_data = update.message.text if update.message else str(update)
            
            # Обрабатываем webhook через YooKassa клиент
            result = self.yookassa.process_webhook(webhook_data)
            
            if result["success"] and result.get("status") == "succeeded":
                payment_id = result["payment_id"]
                
                # Обновляем статус платежа в базе данных
                self.db.update_payment_status(payment_id, "succeeded")
                
                # Получаем информацию о платеже
                payment_info = self.db.get_payment(payment_id)
                if payment_info:
                    user_id = payment_info["user_id"]
                    payment_type = payment_info["payment_type"]
                    
                    # Предоставляем доступ
                    self.db.grant_access(user_id, payment_type)
                    
                    # Уведомляем пользователя
                    success_text = f"""
✅ Платеж успешно обработан!

🎉 Поздравляем! Вам предоставлен доступ к {payment_type}.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации
                    """
                    
                    keyboard = [
                        [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
                        [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
                        [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=success_text,
                        reply_markup=reply_markup
                    )
            
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {e}")
    
    async def give_channel_access_text(self, update):
        """Предоставление доступа к каналу для текстовых сообщений"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли у пользователя доступ
        user_access = self.db.get_user_access(user_id)
        if not user_access:
            await update.message.reply_text("❌ У вас нет активного доступа. Сначала оплатите подписку.")
            return
        
        if not PRIVATE_CHANNEL_ID:
            await update.message.reply_text("❌ Канал не настроен. Обратитесь к администратору.")
            return
        
        # Проверяем, находится ли пользователь уже в канале
        in_channel = await self.channel_manager.check_user_in_channel(user_id)
        
        if in_channel:
            channel_url = self.get_channel_url()
            channel_text = f"""
📺 Закрытый канал Аскезы

Вы уже состоите в нашем закрытом канале!
Перейти: {channel_url}
            """
        else:
            # Добавляем пользователя в канал
            success = await self.channel_manager.add_user_to_channel(user_id)
            if success:
                channel_url = self.get_channel_url()
                channel_text = f"""
📺 Закрытый канал Аскезы

Вы были добавлены в закрытый канал!
Перейти: {channel_url}
                """
            else:
                channel_text = """
📺 Закрытый канал Аскезы

Произошла ошибка при добавлении в канал. Обратитесь к администратору.
                """
        
        await update.message.reply_text(channel_text)
    
    async def give_chat_access_text(self, update):
        """Предоставление доступа к чату для текстовых сообщений"""
        user_id = update.effective_user.id
        
        # Проверяем, есть ли у пользователя доступ
        user_access = self.db.get_user_access(user_id)
        if not user_access:
            await update.message.reply_text("❌ У вас нет активного доступа. Сначала оплатите подписку.")
            return
        
        if not PRIVATE_CHAT_ID:
            await update.message.reply_text("❌ Чат не настроен. Обратитесь к администратору.")
            return
        
        # Проверяем, находится ли пользователь уже в чате
        in_chat = await self.channel_manager.check_user_in_chat(user_id)
        
        if in_chat:
            chat_text = f"""
💬 Закрытый чат Аскезы

Вы уже состоите в нашем закрытом чате!
Перейти: https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}
            """
        else:
            # Добавляем пользователя в чат
            success = await self.channel_manager.add_user_to_chat(user_id)
            if success:
                chat_text = f"""
💬 Закрытый чат Аскезы

Вы были добавлены в закрытый чат!
Перейти: https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}
                """
            else:
                chat_text = """
💬 Закрытый чат Аскезы

Произошла ошибка при добавлении в чат. Обратитесь к администратору.
                """
        
        await update.message.reply_text(chat_text)
    
    async def create_payment_text(self, update, payment_type: str):
        """Создание платежа для текстовых сообщений"""
        user_id = update.effective_user.id
        
        try:
            amount = self.yookassa.get_payment_amount(payment_type)
            description = self.yookassa.get_payment_description(payment_type)
            
            # Создаем платеж в ЮKassa
            payment_result = self.yookassa.create_payment(
                amount=amount,
                description=description,
                return_url=f"https://t.me/your_bot"
            )
            
            if payment_result["success"]:
                # Сохраняем платеж в базу данных
                self.db.create_payment(
                    user_id=user_id,
                    payment_type=payment_type,
                    amount=amount,
                    yookassa_payment_id=payment_result["payment_id"]
                )
                
                payment_text = f"""
💳 Оплата {description}

💰 Сумма: {amount}₽
🆔 ID платежа: {payment_result["payment_id"]}

Перейдите по ссылке для оплаты:
{payment_result["confirmation_url"]}
                """
                
                await update.message.reply_text(payment_text)
            else:
                error_text = f"❌ Ошибка при создании платежа: {payment_result.get('error', 'Неизвестная ошибка')}"
                await update.message.reply_text(error_text)
                
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            error_text = "❌ Произошла ошибка при создании платежа. Попробуйте позже."
            await update.message.reply_text(error_text)
    
    async def show_payment_history_text(self, update):
        """Показ истории платежей для текстовых сообщений"""
        user_id = update.effective_user.id
        
        try:
            logger.info(f"Показываем историю платежей для пользователя {user_id}")
            
            # Получаем все платежи пользователя
            import sqlite3
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT yookassa_payment_id, payment_type, amount, status, created_at, paid_at
                    FROM payments 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                    LIMIT 10
                ''', (user_id,))
                payments = cursor.fetchall()
            
            if not payments:
                history_text = """
📋 История платежей

У вас пока нет платежей.
                """
            else:
                history_text = "📋 История платежей:\n\n"
                
                for payment in payments:
                    payment_id = payment['yookassa_payment_id']
                    payment_type = payment['payment_type']
                    amount = payment['amount']
                    status = payment['status']
                    created_at = payment['created_at']
                    paid_at = payment['paid_at']
                    
                    # Проверяем статус в ЮKassa для pending платежей
                    if status == 'pending':
                        try:
                            status_result = self.yookassa.get_payment_status(payment_id)
                            if status_result["success"]:
                                new_status = status_result["status"]
                                if new_status != status:
                                    # Обновляем статус в БД
                                    self.db.update_payment_status(payment_id, new_status)
                                    status = new_status
                                    logger.info(f"Статус платежа {payment_id} обновлен: {status}")
                        except Exception as e:
                            logger.error(f"Ошибка при проверке статуса платежа {payment_id}: {e}")
                    
                    # Форматируем тип платежа
                    type_name = "Аскеза" if payment_type == "askeza" else "Нумерологический разбор"
                    
                    # Форматируем статус
                    status_emoji = {
                        'pending': '⏳',
                        'succeeded': '✅',
                        'canceled': '❌'
                    }.get(status, '❓')
                    
                    # Форматируем дату
                    from datetime import datetime
                    try:
                        created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
                    except:
                        created_date = created_at
                    
                    history_text += f"{status_emoji} {type_name} - {amount}₽\n"
                    history_text += f"   ID: {payment_id[:8]}...\n"
                    history_text += f"   Дата: {created_date}\n"
                    if paid_at:
                        try:
                            paid_date = datetime.fromisoformat(paid_at.replace('Z', '+00:00')).strftime('%d.%m.%Y %H:%M')
                            history_text += f"   Оплачен: {paid_date}\n"
                        except:
                            pass
                    history_text += "\n"
            
            await update.message.reply_text(history_text)
            
        except Exception as e:
            logger.error(f"Ошибка при показе истории платежей: {e}")
            error_text = "❌ Произошла ошибка при загрузке истории платежей."
            await update.message.reply_text(error_text)
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(f"Ошибка: {context.error}")
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ Произошла ошибка. Попробуйте позже или обратитесь к администратору."
            )
