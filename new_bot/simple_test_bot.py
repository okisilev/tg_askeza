#!/usr/bin/env python3
"""
Простой тестовый бот для проверки работы кнопок
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config

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
    
    print(f"🔍 Получена команда /start от пользователя {user_id}")
    logger.info(f"Получена команда /start от пользователя {user_id}")
    
    # Создаем клавиатуру с кнопками
    keyboard = [
        [InlineKeyboardButton("💰 Оплатить доступ (299 руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
Добро пожаловать, {user.first_name or 'друг'}! 🌸

Это тестовый бот для проверки работы кнопок.

Нажмите на любую кнопку для тестирования.
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ Приветственное сообщение отправлено пользователю {user_id}")

async def handle_pay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки оплаты"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 Получен запрос на оплату от пользователя {user_id}")
    logger.info(f"Получен запрос на оплату от пользователя {user_id}")
    
    await query.edit_message_text(
        "✅ Кнопка оплаты работает!\n\n"
        "Платеж будет создан через ЮKassa API.\n"
        "Проверьте логи для подробностей."
    )
    
    print(f"✅ Обработчик оплаты выполнен для пользователя {user_id}")

async def handle_check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 Получен запрос на проверку платежа от пользователя {user_id}")
    logger.info(f"Получен запрос на проверку платежа от пользователя {user_id}")
    
    await query.edit_message_text(
        "✅ Кнопка проверки платежа работает!\n\n"
        "Проверка статуса будет выполнена через ЮKassa API."
    )
    
    print(f"✅ Обработчик проверки платежа выполнен для пользователя {user_id}")

async def handle_test_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик тестовой кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 Получен запрос на тест от пользователя {user_id}")
    logger.info(f"Получен запрос на тест от пользователя {user_id}")
    
    # Создаем новую клавиатуру
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")],
        [InlineKeyboardButton("🧪 Еще тест", callback_data="test_button")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✅ Тестовая кнопка работает!\n\n"
        "Все обработчики функционируют корректно.\n"
        "Проблема была в основном боте.",
        reply_markup=reply_markup
    )
    
    print(f"✅ Обработчик теста выполнен для пользователя {user_id}")

async def handle_back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки назад"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 Получен запрос назад от пользователя {user_id}")
    logger.info(f"Получен запрос назад от пользователя {user_id}")
    
    # Возвращаемся к главному меню
    keyboard = [
        [InlineKeyboardButton("💰 Оплатить доступ (299 руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 Главное меню\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    
    print(f"✅ Возврат в главное меню для пользователя {user_id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error: {context.error}")
    print(f"❌ Ошибка: {context.error}")

def main():
    """Основная функция запуска бота"""
    print("🚀 Запуск простого тестового бота...")
    print(f"🤖 Токен: {config.BOT_TOKEN[:10]}...")
    
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_pay_callback, pattern="pay"))
    application.add_handler(CallbackQueryHandler(handle_check_payment_callback, pattern="check_payment"))
    application.add_handler(CallbackQueryHandler(handle_test_button_callback, pattern="test_button"))
    application.add_handler(CallbackQueryHandler(handle_back_to_main_callback, pattern="back_to_main"))
    application.add_error_handler(error_handler)

    print("✅ Обработчики зарегистрированы")
    print("🔍 Тестируйте кнопки в боте")
    print("📝 Все действия логируются")
    
    application.run_polling()

if __name__ == '__main__':
    main()
