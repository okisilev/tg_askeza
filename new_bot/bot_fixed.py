#!/usr/bin/env python3
"""
Исправленная версия бота с дополнительным логированием
"""

import logging
import asyncio
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
from yookassa import Configuration, Payment
from yookassa.domain.request import PaymentRequest
from yookassa.domain.response import PaymentResponse
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация ЮKassa
Configuration.account_id = config.YOOKASSA_SHOP_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY

# Инициализация базы данных
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    logger.info(f"Получена команда /start от пользователя {user_id}")
    
    # Добавляем пользователя в базу данных
    try:
        db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        logger.info(f"Пользователь {user_id} добавлен в базу данных")
    except Exception as e:
        logger.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
    
    # Создаем клавиатуру с кнопками оплаты
    keyboard = [
        [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
Добро пожаловать, {user.first_name or 'друг'}! 🌸

Для доступа к закрытому каналу необходимо оплатить подписку за {config.PAYMENT_AMOUNT} рублей.

После оплаты вы получите доступ к эксклюзивным материалам и закрытым обсуждениям.
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    logger.info(f"Приветственное сообщение отправлено пользователю {user_id}")

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    logger.info(f"Получен запрос на создание платежа от пользователя {user_id}")
    
    try:
        # Создаем уникальный ID платежа
        payment_id = str(uuid.uuid4())
        logger.info(f"Создан payment_id: {payment_id}")
        
        # Создаем платеж в ЮKassa
        logger.info(f"Создаем платеж в ЮKassa для пользователя {user_id}")
        payment = Payment.create(PaymentRequest({
            "amount": {
                "value": f"{config.PAYMENT_AMOUNT:.2f}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{context.bot.username}"
            },
            "description": config.PAYMENT_DESCRIPTION,
            "capture": True  # Автоматическое подтверждение платежа
        }, payment_id))
        
        logger.info(f"Платеж создан в ЮKassa: {payment.id}")
        
        # Сохраняем платеж в базу данных
        try:
            db.add_payment(
                user_id=user_id,
                payment_id=payment_id,
                amount=config.PAYMENT_AMOUNT
            )
            logger.info(f"Платеж сохранен в базу данных для пользователя {user_id}")
        except Exception as e:
            logger.error(f"Ошибка при сохранении платежа в БД: {e}")
        
        # Получаем URL для оплаты
        confirmation_url = payment.confirmation.confirmation_url
        logger.info(f"URL для оплаты: {confirmation_url}")
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("💳 Перейти к оплате", url=confirmation_url)],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        payment_text = f"""
💳 Создан платеж на сумму {config.PAYMENT_AMOUNT} рублей

Вы будете перенаправлены на платёжную форму ЮKassa.

После оплаты нажмите кнопку 'Проверить оплату' для подтверждения доступа.
        """
        
        await query.edit_message_text(
            payment_text,
            reply_markup=reply_markup
        )
        
        logger.info(f"Сообщение с платежом отправлено пользователю {user_id}")
        
    except Exception as e:
        logger.error(f"Ошибка при создании платежа для пользователя {user_id}: {e}")
        await query.edit_message_text(
            "❌ Ошибка при создании платежа. Попробуйте позже."
        )

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    logger.info(f"Получен запрос на проверку платежа от пользователя {user_id}")
    
    try:
        # Получаем информацию о платеже из базы данных
        payment_info = db.get_user_payment(user_id)
        
        if not payment_info:
            logger.warning(f"Платеж не найден для пользователя {user_id}")
            await query.edit_message_text("❌ Платеж не найден. Попробуйте начать заново.")
            return
        
        payment_id = payment_info['payment_id']
        logger.info(f"Проверяем статус платежа {payment_id}")
        
        # Проверяем статус платежа в ЮKassa
        payment: PaymentResponse = Payment.find_one(payment_id)
        
        logger.info(f"Статус платежа {payment_id}: {payment.status}")
        
        if payment.status == "succeeded":
            # Обновляем статус в базе данных
            db.update_payment_status(payment_id, "succeeded")
            logger.info(f"Статус платежа {payment_id} обновлен на succeeded")
            
            # Добавляем пользователя в канал
            try:
                # Создаем пригласительную ссылку
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=int(config.PRIVATE_CHANNEL_ID),
                    member_limit=1,
                    expire_date=None
                )
                
                logger.info(f"Пригласительная ссылка создана для пользователя {user_id}")
                
                # Отправляем приглашение пользователю
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"📺 Добро пожаловать в закрытый канал!\n\n{invite_link.invite_link}"
                )
                
                # Обновляем сообщение
                keyboard = [
                    [InlineKeyboardButton("📺 Перейти в канал", url=invite_link.invite_link)],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                success_text = f"""
🎉 Поздравляем! Вы успешно оплатили доступ за {config.PAYMENT_AMOUNT} рублей.

Теперь вы можете:
• Получать эксклюзивные материалы
• Участвовать в закрытых обсуждениях
• Получать персональные консультации

Нажмите кнопку ниже для перехода в канал.
                """
                
                await query.edit_message_text(
                    success_text,
                    reply_markup=reply_markup
                )
                
                logger.info(f"Пользователь {user_id} успешно получил доступ к каналу")
                
            except TelegramError as e:
                logger.error(f"Ошибка при добавлении в канал для пользователя {user_id}: {e}")
                await query.edit_message_text(
                    "❌ Ошибка при добавлении в канал. Обратитесь к администратору."
                )
                
        elif payment.status == "canceled":
            db.update_payment_status(payment_id, "canceled")
            logger.info(f"Платеж {payment_id} отменен")
            await query.edit_message_text(
                "❌ Платеж был отменен. Попробуйте создать новый платеж."
            )
            
        else:
            logger.info(f"Платеж {payment_id} еще не завершен, статус: {payment.status}")
            await query.edit_message_text(
                "⏳ Оплата ещё не завершена. Подождите или попробуйте позже."
            )
            
    except Exception as e:
        logger.error(f"Ошибка при проверке платежа для пользователя {user_id}: {e}")
        await query.edit_message_text("❌ Ошибка проверки платежа. Попробуйте позже.")

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    
    logger.info(f"Получен запрос на главное меню от пользователя {user_id}")
    
    # Создаем клавиатуру с кнопками оплаты
    keyboard = [
        [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
Добро пожаловать, {user.first_name or 'друг'}! 🌸

Для доступа к закрытому каналу необходимо оплатить подписку за {config.PAYMENT_AMOUNT} рублей.

После оплаты вы получите доступ к эксклюзивным материалам и закрытым обсуждениям.
    """
    
    await query.edit_message_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    logger.info(f"Главное меню отправлено пользователю {user_id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error: {context.error}")

def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="pay"))
    application.add_handler(CallbackQueryHandler(check_payment, pattern="check_payment"))
    application.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))
    application.add_error_handler(error_handler)

    print("🚀 Бот запущен...")
    print(f"💰 Сумма оплаты: {config.PAYMENT_AMOUNT} рублей")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("📝 Логирование включено")
    application.run_polling()

if __name__ == '__main__':
    main()
