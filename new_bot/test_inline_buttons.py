#!/usr/bin/env python3
"""
Тест inline кнопок с подробным логированием
"""

import logging
import asyncio
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
    
    print(f"🔍 [START] Получена команда /start от пользователя {user_id}")
    logger.info(f"[START] Получена команда /start от пользователя {user_id}")
    
    # Создаем клавиатуру с inline кнопками
    keyboard = [
        [InlineKeyboardButton("💰 Оплатить доступ (299 руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
        [InlineKeyboardButton("📊 Статус", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
Добро пожаловать, {user.first_name or 'друг'}! 🌸

Это тестовый бот для проверки inline кнопок.

Нажмите на любую кнопку для тестирования.
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [START] Приветственное сообщение отправлено пользователю {user_id}")
    logger.info(f"[START] Приветственное сообщение отправлено пользователю {user_id}")

async def handle_pay_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки оплаты"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [PAY] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [PAY] Callback data: {query.data}")
    logger.info(f"[PAY] Получен callback_query от пользователя {user_id}")
    logger.info(f"[PAY] Callback data: {query.data}")
    
    await query.edit_message_text(
        "✅ Кнопка оплаты работает!\n\n"
        "Платеж будет создан через ЮKassa API.\n"
        "Проверьте логи для подробностей."
    )
    
    print(f"✅ [PAY] Обработчик оплаты выполнен для пользователя {user_id}")
    logger.info(f"[PAY] Обработчик оплаты выполнен для пользователя {user_id}")

async def handle_check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [CHECK] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [CHECK] Callback data: {query.data}")
    logger.info(f"[CHECK] Получен callback_query от пользователя {user_id}")
    logger.info(f"[CHECK] Callback data: {query.data}")
    
    await query.edit_message_text(
        "✅ Кнопка проверки платежа работает!\n\n"
        "Проверка статуса будет выполнена через ЮKassa API."
    )
    
    print(f"✅ [CHECK] Обработчик проверки платежа выполнен для пользователя {user_id}")
    logger.info(f"[CHECK] Обработчик проверки платежа выполнен для пользователя {user_id}")

async def handle_test_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик тестовой кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [TEST] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [TEST] Callback data: {query.data}")
    logger.info(f"[TEST] Получен callback_query от пользователя {user_id}")
    logger.info(f"[TEST] Callback data: {query.data}")
    
    # Создаем новую клавиатуру
    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")],
        [InlineKeyboardButton("🧪 Еще тест", callback_data="test_button")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "✅ Тестовая кнопка работает!\n\n"
        "Все обработчики функционируют корректно.\n"
        "Inline кнопки работают правильно.",
        reply_markup=reply_markup
    )
    
    print(f"✅ [TEST] Обработчик теста выполнен для пользователя {user_id}")
    logger.info(f"[TEST] Обработчик теста выполнен для пользователя {user_id}")

async def handle_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки статуса"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [STATUS] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [STATUS] Callback data: {query.data}")
    logger.info(f"[STATUS] Получен callback_query от пользователя {user_id}")
    logger.info(f"[STATUS] Callback data: {query.data}")
    
    await query.edit_message_text(
        "📊 Статус бота:\n\n"
        "✅ Бот работает\n"
        "✅ Inline кнопки работают\n"
        "✅ Обработчики зарегистрированы\n"
        "✅ Логирование активно"
    )
    
    print(f"✅ [STATUS] Обработчик статуса выполнен для пользователя {user_id}")
    logger.info(f"[STATUS] Обработчик статуса выполнен для пользователя {user_id}")

async def handle_back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки назад"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [BACK] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [BACK] Callback data: {query.data}")
    logger.info(f"[BACK] Получен callback_query от пользователя {user_id}")
    logger.info(f"[BACK] Callback data: {query.data}")
    
    # Возвращаемся к главному меню
    keyboard = [
        [InlineKeyboardButton("💰 Оплатить доступ (299 руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
        [InlineKeyboardButton("📊 Статус", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🏠 Главное меню\n\n"
        "Выберите действие:",
        reply_markup=reply_markup
    )
    
    print(f"✅ [BACK] Возврат в главное меню для пользователя {user_id}")
    logger.info(f"[BACK] Возврат в главное меню для пользователя {user_id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error: {context.error}")
    print(f"❌ Ошибка: {context.error}")

def main():
    """Основная функция запуска бота"""
    print("🚀 Запуск тестового бота для inline кнопок...")
    print(f"🤖 Токен: {config.BOT_TOKEN[:10]}...")
    
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_pay_callback, pattern="pay"))
    application.add_handler(CallbackQueryHandler(handle_check_payment_callback, pattern="check_payment"))
    application.add_handler(CallbackQueryHandler(handle_test_button_callback, pattern="test_button"))
    application.add_handler(CallbackQueryHandler(handle_status_callback, pattern="status"))
    application.add_handler(CallbackQueryHandler(handle_back_to_main_callback, pattern="back_to_main"))
    application.add_error_handler(error_handler)

    print("✅ Обработчики зарегистрированы:")
    print("   • /start - команда старт")
    print("   • pay - кнопка оплаты")
    print("   • check_payment - кнопка проверки")
    print("   • test_button - тестовая кнопка")
    print("   • status - кнопка статуса")
    print("   • back_to_main - кнопка назад")
    print("🔍 Тестируйте inline кнопки в боте")
    print("📝 Все действия логируются")
    
    application.run_polling()

if __name__ == '__main__':
    main()
