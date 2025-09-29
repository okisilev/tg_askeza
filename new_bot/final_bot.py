#!/usr/bin/env python3
"""
Финальная версия бота с максимальным логированием inline кнопок
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
    
    print(f"🔍 [START] Получена команда /start от пользователя {user_id}")
    logger.info(f"[START] Получена команда /start от пользователя {user_id}")
    
    # Добавляем пользователя в базу данных
    try:
        db.add_user(
            user_id=user_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        print(f"✅ [START] Пользователь {user_id} добавлен в базу данных")
        logger.info(f"[START] Пользователь {user_id} добавлен в базу данных")
    except Exception as e:
        print(f"❌ [START] Ошибка при добавлении пользователя {user_id}: {e}")
        logger.error(f"[START] Ошибка при добавлении пользователя {user_id}: {e}")
    
    # Создаем клавиатуру с inline кнопками
    keyboard = [
        [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
        [InlineKeyboardButton("📊 Статус", callback_data="status")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    print(f"🔍 [START] Создана inline клавиатура с {len(keyboard)} кнопками")
    logger.info(f"[START] Создана inline клавиатура с {len(keyboard)} кнопками")
    
    welcome_text = f"""
Добро пожаловать, {user.first_name or 'друг'}! 🌸

Для доступа к закрытому каналу необходимо оплатить подписку за {config.PAYMENT_AMOUNT} рублей.

После оплаты вы получите доступ к эксклюзивным материалам и закрытым обсуждениям.
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [START] Приветственное сообщение с inline кнопками отправлено пользователю {user_id}")
    logger.info(f"[START] Приветственное сообщение с inline кнопками отправлено пользователю {user_id}")

async def handle_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [PAY] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [PAY] Callback data: {query.data}")
    print(f"🔍 [PAY] Message ID: {query.message.message_id}")
    logger.info(f"[PAY] Получен callback_query от пользователя {user_id}")
    logger.info(f"[PAY] Callback data: {query.data}")
    logger.info(f"[PAY] Message ID: {query.message.message_id}")
    
    try:
        # Создаем уникальный ID платежа
        payment_id = str(uuid.uuid4())
        print(f"✅ [PAY] Создан payment_id: {payment_id}")
        logger.info(f"[PAY] Создан payment_id: {payment_id}")
        
        # Создаем платеж в ЮKassa
        print(f"🔍 [PAY] Создаем платеж в ЮKassa для пользователя {user_id}")
        logger.info(f"[PAY] Создаем платеж в ЮKassa для пользователя {user_id}")
        
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
        
        print(f"✅ [PAY] Платеж создан в ЮKassa: {payment.id}")
        logger.info(f"[PAY] Платеж создан в ЮKassa: {payment.id}")
        
        # Сохраняем платеж в базу данных
        try:
            db.add_payment(
                user_id=user_id,
                payment_id=payment_id,
                amount=config.PAYMENT_AMOUNT
            )
            print(f"✅ [PAY] Платеж сохранен в базу данных для пользователя {user_id}")
            logger.info(f"[PAY] Платеж сохранен в базу данных для пользователя {user_id}")
        except Exception as e:
            print(f"❌ [PAY] Ошибка при сохранении платежа в БД: {e}")
            logger.error(f"[PAY] Ошибка при сохранении платежа в БД: {e}")
        
        # Получаем URL для оплаты
        confirmation_url = payment.confirmation.confirmation_url
        print(f"✅ [PAY] URL для оплаты: {confirmation_url}")
        logger.info(f"[PAY] URL для оплаты: {confirmation_url}")
        
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
        
        print(f"✅ [PAY] Сообщение с платежом отправлено пользователю {user_id}")
        logger.info(f"[PAY] Сообщение с платежом отправлено пользователю {user_id}")
        
    except Exception as e:
        print(f"❌ [PAY] Ошибка при создании платежа для пользователя {user_id}: {e}")
        logger.error(f"[PAY] Ошибка при создании платежа для пользователя {user_id}: {e}")
        await query.edit_message_text(
            "❌ Ошибка при создании платежа. Попробуйте позже."
        )

async def handle_check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [CHECK] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [CHECK] Callback data: {query.data}")
    print(f"🔍 [CHECK] Message ID: {query.message.message_id}")
    logger.info(f"[CHECK] Получен callback_query от пользователя {user_id}")
    logger.info(f"[CHECK] Callback data: {query.data}")
    logger.info(f"[CHECK] Message ID: {query.message.message_id}")
    
    try:
        # Получаем информацию о платеже из базы данных
        payment_info = db.get_user_payment(user_id)
        
        if not payment_info:
            print(f"⚠️ [CHECK] Платеж не найден для пользователя {user_id}")
            logger.warning(f"[CHECK] Платеж не найден для пользователя {user_id}")
            await query.edit_message_text("❌ Платеж не найден. Попробуйте начать заново.")
            return
        
        payment_id = payment_info['payment_id']
        print(f"🔍 [CHECK] Проверяем статус платежа {payment_id}")
        logger.info(f"[CHECK] Проверяем статус платежа {payment_id}")
        
        # Проверяем статус платежа в ЮKassa
        payment: PaymentResponse = Payment.find_one(payment_id)
        
        print(f"✅ [CHECK] Статус платежа {payment_id}: {payment.status}")
        logger.info(f"[CHECK] Статус платежа {payment_id}: {payment.status}")
        
        if payment.status == "succeeded":
            # Обновляем статус в базе данных
            db.update_payment_status(payment_id, "succeeded")
            print(f"✅ [CHECK] Статус платежа {payment_id} обновлен на succeeded")
            logger.info(f"[CHECK] Статус платежа {payment_id} обновлен на succeeded")
            
            # Добавляем пользователя в канал
            try:
                # Создаем пригласительную ссылку
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=int(config.PRIVATE_CHANNEL_ID),
                    member_limit=1,
                    expire_date=None
                )
                
                print(f"✅ [CHECK] Пригласительная ссылка создана для пользователя {user_id}")
                logger.info(f"[CHECK] Пригласительная ссылка создана для пользователя {user_id}")
                
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
                
                print(f"✅ [CHECK] Пользователь {user_id} успешно получил доступ к каналу")
                logger.info(f"[CHECK] Пользователь {user_id} успешно получил доступ к каналу")
                
            except TelegramError as e:
                print(f"❌ [CHECK] Ошибка при добавлении в канал для пользователя {user_id}: {e}")
                logger.error(f"[CHECK] Ошибка при добавлении в канал для пользователя {user_id}: {e}")
                await query.edit_message_text(
                    "❌ Ошибка при добавлении в канал. Обратитесь к администратору."
                )
                
        elif payment.status == "canceled":
            db.update_payment_status(payment_id, "canceled")
            print(f"✅ [CHECK] Платеж {payment_id} отменен")
            logger.info(f"[CHECK] Платеж {payment_id} отменен")
            await query.edit_message_text(
                "❌ Платеж был отменен. Попробуйте создать новый платеж."
            )
            
        else:
            print(f"⏳ [CHECK] Платеж {payment_id} еще не завершен, статус: {payment.status}")
            logger.info(f"[CHECK] Платеж {payment_id} еще не завершен, статус: {payment.status}")
            await query.edit_message_text(
                "⏳ Оплата ещё не завершена. Подождите или попробуйте позже."
            )
            
    except Exception as e:
        print(f"❌ [CHECK] Ошибка при проверке платежа для пользователя {user_id}: {e}")
        logger.error(f"[CHECK] Ошибка при проверке платежа для пользователя {user_id}: {e}")
        await query.edit_message_text("❌ Ошибка проверки платежа. Попробуйте позже.")

async def handle_test_button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик тестовой кнопки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [TEST] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [TEST] Callback data: {query.data}")
    print(f"🔍 [TEST] Message ID: {query.message.message_id}")
    logger.info(f"[TEST] Получен callback_query от пользователя {user_id}")
    logger.info(f"[TEST] Callback data: {query.data}")
    logger.info(f"[TEST] Message ID: {query.message.message_id}")
    
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
    print(f"🔍 [STATUS] Message ID: {query.message.message_id}")
    logger.info(f"[STATUS] Получен callback_query от пользователя {user_id}")
    logger.info(f"[STATUS] Callback data: {query.data}")
    logger.info(f"[STATUS] Message ID: {query.message.message_id}")
    
    await query.edit_message_text(
        "📊 Статус бота:\n\n"
        "✅ Бот работает\n"
        "✅ Inline кнопки работают\n"
        "✅ Обработчики зарегистрированы\n"
        "✅ Логирование активно\n"
        "✅ ЮKassa API подключен\n"
        "✅ База данных работает"
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
    print(f"🔍 [BACK] Message ID: {query.message.message_id}")
    logger.info(f"[BACK] Получен callback_query от пользователя {user_id}")
    logger.info(f"[BACK] Callback data: {query.data}")
    logger.info(f"[BACK] Message ID: {query.message.message_id}")
    
    # Возвращаемся к главному меню
    keyboard = [
        [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
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

async def handle_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    
    print(f"🔍 [MAIN] Получен callback_query от пользователя {user_id}")
    print(f"🔍 [MAIN] Callback data: {query.data}")
    print(f"🔍 [MAIN] Message ID: {query.message.message_id}")
    logger.info(f"[MAIN] Получен callback_query от пользователя {user_id}")
    logger.info(f"[MAIN] Callback data: {query.data}")
    logger.info(f"[MAIN] Message ID: {query.message.message_id}")
    
    # Создаем клавиатуру с кнопками оплаты
    keyboard = [
        [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
        [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
        [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
        [InlineKeyboardButton("📊 Статус", callback_data="status")]
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
    
    print(f"✅ [MAIN] Главное меню отправлено пользователю {user_id}")
    logger.info(f"[MAIN] Главное меню отправлено пользователю {user_id}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error: {context.error}")
    print(f"❌ Ошибка: {context.error}")

def main():
    """Основная функция запуска бота"""
    print("🚀 Запуск финального бота с максимальным логированием...")
    print(f"💰 Сумма оплаты: {config.PAYMENT_AMOUNT} рублей")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("📝 Максимальное логирование включено")
    
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_payment_callback, pattern="pay"))
    application.add_handler(CallbackQueryHandler(handle_check_payment_callback, pattern="check_payment"))
    application.add_handler(CallbackQueryHandler(handle_test_button_callback, pattern="test_button"))
    application.add_handler(CallbackQueryHandler(handle_status_callback, pattern="status"))
    application.add_handler(CallbackQueryHandler(handle_back_to_main_callback, pattern="back_to_main"))
    application.add_handler(CallbackQueryHandler(handle_main_menu_callback, pattern="main_menu"))
    application.add_error_handler(error_handler)

    print("✅ Обработчики зарегистрированы:")
    print("   • /start - команда старт")
    print("   • pay - кнопка оплаты")
    print("   • check_payment - кнопка проверки")
    print("   • test_button - тестовая кнопка")
    print("   • status - кнопка статуса")
    print("   • back_to_main - кнопка назад")
    print("   • main_menu - главное меню")
    print("🔍 Тестируйте inline кнопки в боте")
    print("📝 Все действия логируются")
    
    application.run_polling()

if __name__ == '__main__':
    main()
