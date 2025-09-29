#!/usr/bin/env python3
"""
Тест работы кнопки оплаты
"""

import asyncio
import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    user_id = user.id
    
    # Добавляем пользователя в базу данных
    db = Database()
    db.add_user(
        user_id=user_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
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

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    try:
        print(f"🔍 Обработчик платежа вызван для пользователя {user_id}")
        
        # Простое сообщение для теста
        await query.edit_message_text(
            "✅ Кнопка оплаты работает!\n\n"
            "Платеж будет создан через ЮKassa API.\n"
            "Проверьте логи бота для подробностей."
        )
        
        print(f"✅ Обработчик платежа выполнен для пользователя {user_id}")
        
    except Exception as e:
        print(f"❌ Ошибка в обработчике платежа: {e}")
        await query.edit_message_text(
            "❌ Ошибка при создании платежа. Попробуйте позже."
        )

async def check_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ Кнопка проверки платежа работает!\n\n"
        "Проверка статуса будет выполнена через ЮKassa API."
    )

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
    application.add_error_handler(error_handler)

    print("🚀 Тестовый бот запущен...")
    print(f"💰 Сумма оплаты: {config.PAYMENT_AMOUNT} рублей")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("🔍 Тестируйте кнопки в боте")
    application.run_polling()

if __name__ == '__main__':
    main()
