

#!/usr/bin/env python3
"""
Упрощенная версия бота без планировщика для тестирования
"""

import logging
import asyncio
import uuid
from datetime import datetime, timedelta
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
        db.update_user_activity(user_id)
        print(f"✅ [START] Пользователь {user_id} добавлен в базу данных")
        logger.info(f"[START] Пользователь {user_id} добавлен в базу данных")
    except Exception as e:
        print(f"❌ [START] Ошибка при добавлении пользователя {user_id}: {e}")
        logger.error(f"[START] Ошибка при добавлении пользователя {user_id}: {e}")
    
    # Проверяем статус подписки
    is_subscribed = db.is_subscription_active(user_id)
    
    if is_subscribed:
        # Пользователь уже подписан
        subscription = db.get_user_subscription(user_id)
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        days_left = (expires_at - datetime.now()).days
        
        keyboard = [
            [InlineKeyboardButton("📺 Перейти в канал", url=f"https://t.me/c/{config.PRIVATE_CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🎉 Добро пожаловать обратно!

У вас есть активная подписка до {expires_at.strftime('%d.%m.%Y')}
Осталось дней: {days_left}

Нажмите кнопку ниже для перехода в приватный канал.
        """
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
    else:
        # Пользователь не подписан
        keyboard = [
            [InlineKeyboardButton(f"💰 Подписаться ({config.SUBSCRIPTION_PRICE} руб.)", callback_data="subscribe")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("ℹ️ О подписке", callback_data="about_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = config.WELCOME_MESSAGE.format(price=config.SUBSCRIPTION_PRICE)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup
        )
    
    print(f"✅ [START] Приветственное сообщение отправлено пользователю {user_id}")
    logger.info(f"[START] Приветственное сообщение отправлено пользователю {user_id}")

async def handle_subscribe_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [SUBSCRIBE] Получен запрос на подписку от пользователя {user_id}")
    logger.info(f"[SUBSCRIBE] Получен запрос на подписку от пользователя {user_id}")
    
    try:
        # Создаем платеж в ЮKassa (без предварительного ID)
        print(f"🔍 [SUBSCRIBE] Создаем платеж в ЮKassa для пользователя {user_id}")
        logger.info(f"[SUBSCRIBE] Создаем платеж в ЮKassa для пользователя {user_id}")
        
        payment = Payment.create({
            "amount": {
                "value": f"{config.SUBSCRIPTION_PRICE:.2f}",
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
        })
        
        # Получаем ID платежа от ЮKassa
        payment_id = payment.id
        print(f"✅ [SUBSCRIBE] Создан payment_id: {payment_id}")
        logger.info(f"[SUBSCRIBE] Создан payment_id: {payment_id}")
        
        print(f"✅ [SUBSCRIBE] Платеж создан в ЮKassa: {payment.id}")
        logger.info(f"[SUBSCRIBE] Платеж создан в ЮKassa: {payment.id}")
        
        # Сохраняем платеж в базу данных
        try:
            db.add_payment(
                user_id=user_id,
                payment_id=payment_id,
                amount=config.SUBSCRIPTION_PRICE
            )
            print(f"✅ [SUBSCRIBE] Платеж сохранен в базу данных для пользователя {user_id}")
            logger.info(f"[SUBSCRIBE] Платеж сохранен в базу данных для пользователя {user_id}")
        except Exception as e:
            print(f"❌ [SUBSCRIBE] Ошибка при сохранении платежа в БД: {e}")
            logger.error(f"[SUBSCRIBE] Ошибка при сохранении платежа в БД: {e}")
        
        # Получаем URL для оплаты
        confirmation_url = payment.confirmation.confirmation_url
        print(f"✅ [SUBSCRIBE] URL для оплаты: {confirmation_url}")
        logger.info(f"[SUBSCRIBE] URL для оплаты: {confirmation_url}")
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("💳 Перейти к оплате", url=confirmation_url)],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        payment_text = f"""
💳 Создан платеж на подписку за {config.SUBSCRIPTION_PRICE} рублей

Подписка действует {config.SUBSCRIPTION_DAYS} дней.

Вы будете перенаправлены на платёжную форму ЮKassa.
После оплаты нажмите кнопку 'Проверить оплату' для активации подписки.
        """
        
        await query.edit_message_text(
            payment_text,
            reply_markup=reply_markup
        )
        
        print(f"✅ [SUBSCRIBE] Сообщение с платежом отправлено пользователю {user_id}")
        logger.info(f"[SUBSCRIBE] Сообщение с платежом отправлено пользователю {user_id}")
        
    except Exception as e:
        print(f"❌ [SUBSCRIBE] Ошибка при создании платежа для пользователя {user_id}: {e}")
        logger.error(f"[SUBSCRIBE] Ошибка при создании платежа для пользователя {user_id}: {e}")
        await query.edit_message_text(
            "❌ Ошибка при создании платежа. Попробуйте позже."
        )

async def handle_check_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки платежа"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [CHECK] Получен запрос на проверку платежа от пользователя {user_id}")
    logger.info(f"[CHECK] Получен запрос на проверку платежа от пользователя {user_id}")
    
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
            
            # Создаем подписку
            try:
                db.create_subscription(user_id, payment_id, config.SUBSCRIPTION_PRICE)
                print(f"✅ [CHECK] Подписка создана для пользователя {user_id}")
                logger.info(f"[CHECK] Подписка создана для пользователя {user_id}")
                
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
                    text=f"📺 Добро пожаловать в приватный канал!\n\n{invite_link.invite_link}"
                )
                
                # Обновляем сообщение
                keyboard = [
                    [InlineKeyboardButton("📺 Перейти в канал", url=invite_link.invite_link)],
                    [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                success_text = f"""
🎉 Поздравляем! Ваша подписка активирована!

Подписка действует {config.SUBSCRIPTION_DAYS} дней.
Вы получили доступ к эксклюзивным материалам и закрытым обсуждениям.

Нажмите кнопку ниже для перехода в канал.
                """
                
                await query.edit_message_text(
                    success_text,
                    reply_markup=reply_markup
                )
                
                print(f"✅ [CHECK] Пользователь {user_id} успешно получил подписку")
                logger.info(f"[CHECK] Пользователь {user_id} успешно получил подписку")
                
            except TelegramError as e:
                print(f"❌ [CHECK] Ошибка при создании подписки для пользователя {user_id}: {e}")
                logger.error(f"[CHECK] Ошибка при создании подписки для пользователя {user_id}: {e}")
                await query.edit_message_text(
                    "❌ Ошибка при активации подписки. Обратитесь к администратору."
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

async def handle_my_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик проверки статуса подписки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [STATUS] Получен запрос на статус от пользователя {user_id}")
    logger.info(f"[STATUS] Получен запрос на статус от пользователя {user_id}")
    
    subscription = db.get_user_subscription(user_id)
    
    if subscription:
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        days_left = (expires_at - datetime.now()).days
        
        if days_left > 0:
            status_text = f"""
📊 Ваш статус подписки:

✅ Подписка активна
📅 Действует до: {expires_at.strftime('%d.%m.%Y')}
⏰ Осталось дней: {days_left}

Вы можете продолжать пользоваться всеми возможностями приватного канала.
            """
        else:
            status_text = f"""
📊 Ваш статус подписки:

❌ Подписка истекла
📅 Истекла: {expires_at.strftime('%d.%m.%Y')}

Для продолжения доступа необходимо продлить подписку.
            """
    else:
        status_text = """
📊 Ваш статус подписки:

❌ Подписка отсутствует

Для доступа к приватному каналу необходимо оформить подписку.
        """
    
    keyboard = [
        [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        status_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [STATUS] Статус отправлен пользователю {user_id}")
    logger.info(f"[STATUS] Статус отправлен пользователю {user_id}")

async def handle_renew_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик продления подписки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [RENEW] Получен запрос на продление подписки от пользователя {user_id}")
    logger.info(f"[RENEW] Получен запрос на продление подписки от пользователя {user_id}")
    
    # Перенаправляем на создание новой подписки
    await handle_subscribe_callback(update, context)

async def handle_about_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик информации о подписке"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [ABOUT] Получен запрос об информации о подписке от пользователя {user_id}")
    logger.info(f"[ABOUT] Получен запрос об информации о подписке от пользователя {user_id}")
    
    about_text = f"""
ℹ️ О подписке:

💰 Стоимость: {config.SUBSCRIPTION_PRICE} рублей
📅 Длительность: {config.SUBSCRIPTION_DAYS} дней
📺 Доступ: Приватный канал с эксклюзивными материалами

🎁 Что вы получите:
• Эксклюзивные материалы
• Закрытые обсуждения
• Персональные консультации
• Уведомления о новых материалах

⚠️ Важно:
• Подписка продлевается автоматически
• За {config.WARNING_DAYS} дня до окончания вы получите уведомление
• Доступ к каналу предоставляется сразу после оплаты
    """
    
    keyboard = [
        [InlineKeyboardButton(f"💰 Подписаться ({config.SUBSCRIPTION_PRICE} руб.)", callback_data="subscribe")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        about_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [ABOUT] Информация о подписке отправлена пользователю {user_id}")
    logger.info(f"[ABOUT] Информация о подписке отправлена пользователю {user_id}")

async def handle_main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик главного меню"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    user_id = user.id
    
    print(f"🔍 [MAIN] Получен запрос на главное меню от пользователя {user_id}")
    logger.info(f"[MAIN] Получен запрос на главное меню от пользователя {user_id}")
    
    # Проверяем статус подписки
    is_subscribed = db.is_subscription_active(user_id)
    
    if is_subscribed:
        subscription = db.get_user_subscription(user_id)
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        days_left = (expires_at - datetime.now()).days
        
        keyboard = [
            [InlineKeyboardButton("📺 Перейти в канал", url=f"https://t.me/c/{config.PRIVATE_CHANNEL_ID[1:]}")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🏠 Главное меню

У вас есть активная подписка до {expires_at.strftime('%d.%m.%Y')}
Осталось дней: {days_left}
        """
    else:
        keyboard = [
            [InlineKeyboardButton(f"💰 Подписаться ({config.SUBSCRIPTION_PRICE} руб.)", callback_data="subscribe")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("ℹ️ О подписке", callback_data="about_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = f"""
🏠 Главное меню

Получите доступ к эксклюзивным материалам и закрытым обсуждениям.
Подписка на {config.SUBSCRIPTION_DAYS} дней за {config.SUBSCRIPTION_PRICE} рублей.
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
    print("🚀 Запуск упрощенного бота с подписками...")
    print(f"💰 Стоимость подписки: {config.SUBSCRIPTION_PRICE} рублей")
    print(f"📅 Длительность: {config.SUBSCRIPTION_DAYS} дней")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("📝 Логирование включено")
    
    try:
        application = Application.builder().token(config.BOT_TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_subscribe_callback, pattern="subscribe"))
        application.add_handler(CallbackQueryHandler(handle_check_payment_callback, pattern="check_payment"))
        application.add_handler(CallbackQueryHandler(handle_my_status_callback, pattern="my_status"))
        application.add_handler(CallbackQueryHandler(handle_renew_subscription_callback, pattern="renew_subscription"))
        application.add_handler(CallbackQueryHandler(handle_about_subscription_callback, pattern="about_subscription"))
        application.add_handler(CallbackQueryHandler(handle_main_menu_callback, pattern="main_menu"))
        application.add_error_handler(error_handler)

        print("✅ Обработчики зарегистрированы:")
        print("   • /start - команда старт")
        print("   • subscribe - подписка")
        print("   • check_payment - проверка платежа")
        print("   • my_status - статус подписки")
        print("   • renew_subscription - продление подписки")
        print("   • about_subscription - информация о подписке")
        print("   • main_menu - главное меню")
        print("🔍 Тестируйте бота")
        print("📝 Все действия логируются")
        
        # Запускаем бота
        application.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()
