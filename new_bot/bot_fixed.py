#!/usr/bin/env python3
"""
Исправленная версия бота с правильным API
"""

import logging
import asyncio
import uuid
import os
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import TelegramError
from yookassa import Configuration, Payment
from yookassa.domain.request import PaymentRequest
from yookassa.domain.response import PaymentResponse
from config import config
from database import Database

# Получаем путь к директории, где находится этот скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

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

    # Отправляем видео
    try:
        print(f"🎥 [START] Отправляем видео пользователю {user_id}")
        logger.info(f"[START] Отправляем видео пользователю {user_id}")
        
        # Формируем абсолютный путь к файлу видео
        video_path = os.path.join(SCRIPT_DIR, "start.mp4")
        print(f"📁 [START] Путь к видео: {video_path}")
        
        with open(video_path, "rb") as video_file:
            await context.bot.send_video(
                chat_id=user_id,
                video=video_file,
                caption="Добро пожаловать! 🌸"
            )
        
        print(f"✅ [START] Видео отправлено пользователю {user_id}")
        logger.info(f"[START] Видео отправлено пользователю {user_id}")
        
    except FileNotFoundError:
        print(f"❌ [START] Файл start.mp4 не найден")
        logger.error(f"[START] Файл start.mp4 не найден")
    except Exception as e:
        print(f"❌ [START] Ошибка при отправке видео пользователю {user_id}: {e}")
        logger.error(f"[START] Ошибка при отправке видео пользователю {user_id}: {e}")

    # Отправляем приветственное сообщение
    try:
        welcome_text = f"""Меня зовут, Ольга🌸 И я любитель аскез, данную практику я использую уже целых 4 года😍 даже прошла по ней обучение, чтоб знать все нюансы! Из всех сотни практик, которые я когда либо пробовала, аскеза моя самая любимая!💕

Во-первых, ты попробуешь, а как может быть по другому?!☀️
Во-вторых, ты начнешь верить в чудо, потому что желания могут исполняться самым волшебным образом💫
В третьих, твоя жизнь не станет прежней!⭐️

Я жду тебя, {user.first_name}!🫂"""
        
        print(f"💬 [START] Отправляем приветственное сообщение пользователю {user_id}")
        logger.info(f"[START] Отправляем приветственное сообщение пользователю {user_id}")
        
        await context.bot.send_message(
            chat_id=user_id,
            text=welcome_text
        )
        
        print(f"✅ [START] Приветственное сообщение отправлено пользователю {user_id}")
        logger.info(f"[START] Приветственное сообщение отправлено пользователю {user_id}")
        
    except Exception as e:
        print(f"❌ [START] Ошибка при отправке приветственного сообщения пользователю {user_id}: {e}")
        logger.error(f"[START] Ошибка при отправке приветственного сообщения пользователю {user_id}: {e}")

    # Проверяем статус подписки и показываем соответствующее меню
    is_subscribed = db.is_subscription_active(user_id)
    
    if is_subscribed:
        # Пользователь уже подписан
        subscription = db.get_user_subscription(user_id)
        expires_at = datetime.fromisoformat(subscription['expires_at'])
        days_left = (expires_at - datetime.now()).days
        
        # Создаем новую пригласительную ссылку для доступа к каналу
        try:
            print(f"🔗 [START] Создаем пригласительную ссылку для пользователя {user_id}")
            logger.info(f"[START] Создаем пригласительную ссылку для пользователя {user_id}")
            
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=int(config.PRIVATE_CHANNEL_ID),
                member_limit=1,
                expire_date=None
            )
            
            print(f"✅ [START] Пригласительная ссылка создана для пользователя {user_id}")
            logger.info(f"[START] Пригласительная ссылка создана для пользователя {user_id}")
            
            keyboard = [
                [InlineKeyboardButton("📺 Перейти в канал", url=invite_link.invite_link)],
                [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
                [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            status_text = f"""
🎉 Добро пожаловать обратно!

У вас есть активная подписка до {expires_at.strftime('%d.%m.%Y')}
Осталось дней: {days_left}

Нажмите кнопку ниже для перехода в приватный канал.
            """
            
            await context.bot.send_message(
                chat_id=user_id,
                text=status_text,
                reply_markup=reply_markup
            )
            
        except Exception as e:
            print(f"❌ [START] Ошибка при создании пригласительной ссылки для пользователя {user_id}: {e}")
            logger.error(f"[START] Ошибка при создании пригласительной ссылки для пользователя {user_id}: {e}")
            
            # Fallback - используем статичную ссылку
            keyboard = [
                [InlineKeyboardButton("📺 Перейти в канал", url=f"https://t.me/c/{config.PRIVATE_CHANNEL_ID[1:]}")],
                [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
                [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            status_text = f"""
🎉 Добро пожаловать обратно!

У вас есть активная подписка до {expires_at.strftime('%d.%m.%Y')}
Осталось дней: {days_left}

Нажмите кнопку ниже для перехода в приватный канал.
            """
            
            await context.bot.send_message(
                chat_id=user_id,
                text=status_text,
                reply_markup=reply_markup
            )
    else:
        # Пользователь не подписан
        keyboard = [
            [InlineKeyboardButton("💎 Тарифы", callback_data="tariffs")],
            [InlineKeyboardButton("📖 Об Аскезе", callback_data="about_askeza")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("ℹ️ О подписке", callback_data="about_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        menu_text = """
🌸 Добро пожаловать в Аскезу!

Получите доступ к эксклюзивным материалам, закрытым обсуждениям и персональным консультациям.

Нажмите "💎 Тарифы" чтобы выбрать подходящий тариф подписки.
        """
        
        await context.bot.send_message(
            chat_id=user_id,
            text=menu_text,
            reply_markup=reply_markup
        )
    
    print(f"✅ [START] Приветственное сообщение отправлено пользователю {user_id}")
    logger.info(f"[START] Приветственное сообщение отправлено пользователю {user_id}")

async def handle_subscribe_askeza_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки Аскеза"""
    await create_payment(update, context, "askeza", config.ASKEZA_PRICE, config.ASKEZA_DESCRIPTION)

async def handle_subscribe_draft_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки Аскеза+черновик"""
    await create_payment(update, context, "draft", config.ASKEZA_DRAFT_PRICE, config.ASKEZA_DRAFT_DESCRIPTION)

async def handle_subscribe_numerology_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки Аскеза+Нумерология"""
    await create_payment(update, context, "numerology", config.ASKEZA_NUMEROLOGY_PRICE, config.ASKEZA_NUMEROLOGY_DESCRIPTION)

async def create_payment(update: Update, context: ContextTypes.DEFAULT_TYPE, subscription_type: str, price: float, description: str):
    """Создание платежа для подписки"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [SUBSCRIBE] Получен запрос на подписку {subscription_type} от пользователя {user_id}")
    logger.info(f"[SUBSCRIBE] Получен запрос на подписку {subscription_type} от пользователя {user_id}")
    
    try:
        # Создаем платеж в ЮKassa (без предварительного ID)
        print(f"🔍 [SUBSCRIBE] Создаем платеж в ЮKassa для пользователя {user_id}")
        logger.info(f"[SUBSCRIBE] Создаем платеж в ЮKassa для пользователя {user_id}")
        
        payment = Payment.create({
            "amount": {
                "value": f"{price:.2f}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{context.bot.username}"
            },
            "description": description,
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
                amount=price
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
💳 Создан платеж на сумму {price} рублей

{description}

Вы будете перенаправлены на платёжную форму ЮKassa.

После оплаты нажмите кнопку 'Проверить оплату' для подтверждения доступа.
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
            
            # Определяем тип подписки по сумме
            amount = payment_info['amount']
            if amount == config.ASKEZA_PRICE:
                subscription_type = "askeza"
                subscription_name = "Аскеза"
            elif amount == config.ASKEZA_NUMEROLOGY_PRICE:
                subscription_type = "numerology"
                subscription_name = "Аскеза+Нумерология"
            else:
                subscription_type = "askeza"
                subscription_name = "Аскеза"
            
            # Создаем подписку
            try:
                db.create_subscription(user_id, payment_id, amount, subscription_type)
                print(f"✅ [CHECK] Подписка {subscription_name} создана для пользователя {user_id}")
                logger.info(f"[CHECK] Подписка {subscription_name} создана для пользователя {user_id}")
                
                # Отправляем уведомления о успешной оплате
                try:
                    # Уведомление пользователю
                    user_notification = f"""
🎉 Поздравляем! Оплата прошла успешно!

💰 Сумма: {amount} рублей
📦 Подписка: {subscription_name}
📅 Длительность: {config.SUBSCRIPTION_DAYS} дней
⏰ Активна до: {(datetime.now() + timedelta(days=config.SUBSCRIPTION_DAYS)).strftime('%d.%m.%Y %H:%M')}

✅ Ваш доступ к закрытому каналу активирован!
                    """
                    
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=user_notification
                    )
                    
                    print(f"✅ [CHECK] Уведомление пользователю {user_id} отправлено")
                    logger.info(f"[CHECK] Уведомление пользователю {user_id} отправлено")
                    
                    # Уведомление админу
                    admin_notification = f"""
🔔 Новая успешная оплата!

👤 Пользователь: {query.from_user.first_name} {query.from_user.last_name or ''}
🆔 ID: {user_id}
📱 Username: @{query.from_user.username or 'не указан'}
💰 Сумма: {amount} рублей
📦 Подписка: {subscription_name}
📅 Длительность: {config.SUBSCRIPTION_DAYS} дней
🆔 Payment ID: {payment_id}
⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
                    """
                    
                    # Отправляем админу
                    await context.bot.send_message(
                        chat_id=config.ADMIN_ID,
                        text=admin_notification
                    )
                    
                    print(f"✅ [CHECK] Уведомление админу отправлено")
                    logger.info(f"[CHECK] Уведомление админу отправлено")
                    
                except TelegramError as e:
                    print(f"❌ [CHECK] Ошибка при отправке уведомлений: {e}")
                    logger.error(f"[CHECK] Ошибка при отправке уведомлений: {e}")
                
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
            # Создаем новую пригласительную ссылку для активной подписки
            try:
                print(f"🔗 [STATUS] Создаем пригласительную ссылку для пользователя {user_id}")
                logger.info(f"[STATUS] Создаем пригласительную ссылку для пользователя {user_id}")
                
                invite_link = await context.bot.create_chat_invite_link(
                    chat_id=int(config.PRIVATE_CHANNEL_ID),
                    member_limit=1,
                    expire_date=None
                )
                
                print(f"✅ [STATUS] Пригласительная ссылка создана для пользователя {user_id}")
                logger.info(f"[STATUS] Пригласительная ссылка создана для пользователя {user_id}")
                
                status_text = f"""
📊 Ваш статус подписки:

✅ Подписка активна
📅 Действует до: {expires_at.strftime('%d.%m.%Y')}
⏰ Осталось дней: {days_left}

Вы можете продолжать пользоваться всеми возможностями приватного канала.
                """
                
                keyboard = [
                    [InlineKeyboardButton("📺 Перейти в канал", url=invite_link.invite_link)],
                    [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
                
            except Exception as e:
                print(f"❌ [STATUS] Ошибка при создании пригласительной ссылки для пользователя {user_id}: {e}")
                logger.error(f"[STATUS] Ошибка при создании пригласительной ссылки для пользователя {user_id}: {e}")
                
                status_text = f"""
📊 Ваш статус подписки:

✅ Подписка активна
📅 Действует до: {expires_at.strftime('%d.%m.%Y')}
⏰ Осталось дней: {days_left}

Вы можете продолжать пользоваться всеми возможностями приватного канала.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")],
                    [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
                ]
        else:
            status_text = f"""
📊 Ваш статус подписки:

❌ Подписка истекла
📅 Истекла: {expires_at.strftime('%d.%m.%Y')}

Для продолжения доступа необходимо продлить подписку.
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Продлить подписку", callback_data="renew_subscription")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
            ]
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
    
    # Показываем меню с кнопками оплаты
    keyboard = [
        [InlineKeyboardButton(f"🌸 Аскеза - {config.ASKEZA_PRICE} руб.", callback_data="subscribe_askeza")],
        [InlineKeyboardButton(f"🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} руб.", callback_data="subscribe_draft")],
        [InlineKeyboardButton(f"🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} руб.", callback_data="subscribe_numerology")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    renew_text = f"""
🔄 Продление подписки

Выберите подходящий тариф для продления:

🌸 Аскеза - {config.ASKEZA_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• 30 дней подписки

🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Черновик для работы с аскезой
• 30 дней подписки

🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Нумерологический разбор любого запроса
    """
    
    await query.edit_message_text(
        renew_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [RENEW] Меню продления отправлено пользователю {user_id}")
    logger.info(f"[RENEW] Меню продления отправлено пользователю {user_id}")

async def handle_about_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик информации о подписке"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [ABOUT] Получен запрос об информации о подписке от пользователя {user_id}")
    logger.info(f"[ABOUT] Получен запрос об информации о подписке от пользователя {user_id}")
    
    about_text = f"""
ℹ️ О подписке:

🌸 Аскеза - {config.ASKEZA_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• 30 дней подписки

🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Черновик для работы с аскезой
• 30 дней подписки

🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Нумерологический разбор любого запроса

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
        [InlineKeyboardButton(f"🌸 Аскеза - {config.ASKEZA_PRICE} руб.", callback_data="subscribe_askeza")],
        [InlineKeyboardButton(f"🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} руб.", callback_data="subscribe_draft")],
        [InlineKeyboardButton(f"🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} руб.", callback_data="subscribe_numerology")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        about_text,
        reply_markup=reply_markup
    )
    
    print(f"✅ [ABOUT] Информация о подписке отправлена пользователю {user_id}")
    logger.info(f"[ABOUT] Информация о подписке отправлена пользователю {user_id}")

async def handle_about_askeza_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик информации об Аскезе"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [ABOUT_ASKEZA] Получен запрос об Аскезе от пользователя {user_id}")
    logger.info(f"[ABOUT_ASKEZA] Получен запрос об Аскезе от пользователя {user_id}")
    
    # Отправляем видео
    try:
        print(f"🎥 [ABOUT_ASKEZA] Отправляем видео пользователю {user_id}")
        logger.info(f"[ABOUT_ASKEZA] Отправляем видео пользователю {user_id}")
        
        # Формируем абсолютный путь к файлу видео
        video_path = os.path.join(SCRIPT_DIR, "aboute.mp4")
        print(f"📁 [ABOUT_ASKEZA] Путь к видео: {video_path}")
        
        with open(video_path, "rb") as video_file:
            await context.bot.send_video(
                chat_id=user_id,
                video=video_file
                #caption="📖 Об Аскезе"
            )
        
        print(f"✅ [ABOUT_ASKEZA] Видео отправлено пользователю {user_id}")
        logger.info(f"[ABOUT_ASKEZA] Видео отправлено пользователю {user_id}")
        
    except FileNotFoundError:
        print(f"❌ [ABOUT_ASKEZA] Файл aboute.mp4 не найден")
        logger.error(f"[ABOUT_ASKEZA] Файл aboute.mp4 не найден")
    except Exception as e:
        print(f"❌ [ABOUT_ASKEZA] Ошибка при отправке видео пользователю {user_id}: {e}")
        logger.error(f"[ABOUT_ASKEZA] Ошибка при отправке видео пользователю {user_id}: {e}")
    
    # Отправляем текст с кнопками
    about_askeza_text = """📖 Об Аскезе

Аскеза - духовная практика подобная посту, только здесь можно брать ее каждый месяц!✨ вы добровольно на определенный период, либо отказываетесь от чего-то, либо внедряете в свою жизнь хорошую привычку и выработанная энергия идет на исполнение вашего💫

Желание может быть абсолютно любым: материальное, духовное, психологическое и даже физическое, чем аскеза крута, что вы можете загадать даже выздоровление своего близкого!😻"""
    
    keyboard = [
        [InlineKeyboardButton(f"🌸 Аскеза - {config.ASKEZA_PRICE} руб.", callback_data="subscribe_askeza")],
        [InlineKeyboardButton(f"🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} руб.", callback_data="subscribe_draft")],
        [InlineKeyboardButton(f"🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} руб.", callback_data="subscribe_numerology")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=about_askeza_text,
            reply_markup=reply_markup
        )
        print(f"✅ [ABOUT_ASKEZA] Информация об Аскезе отправлена пользователю {user_id}")
        logger.info(f"[ABOUT_ASKEZA] Информация об Аскезе отправлена пользователю {user_id}")
    except Exception as e:
        print(f"❌ [ABOUT_ASKEZA] Ошибка при отправке сообщения пользователю {user_id}: {e}")
        logger.error(f"[ABOUT_ASKEZA] Ошибка при отправке сообщения пользователю {user_id}: {e}")

async def handle_tariffs_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения тарифов"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    print(f"🔍 [TARIFFS] Получен запрос на отображение тарифов от пользователя {user_id}")
    logger.info(f"[TARIFFS] Получен запрос на отображение тарифов от пользователя {user_id}")
    
    tariffs_text = f"""
💎 Доступные тарифы:

🌸 Аскеза - {config.ASKEZA_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• 30 дней подписки

🌸 Аскеза+проверка черновика - {config.ASKEZA_DRAFT_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Проверка вашего черновика аскезы
• 30 дней подписки

🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• Нумерологический разбор любого запроса
• 30 дней подписки

Выберите подходящий тариф:
    """
    
    keyboard = [
        [InlineKeyboardButton(f"🌸 Аскеза - {config.ASKEZA_PRICE} руб.", callback_data="subscribe_askeza")],
        [InlineKeyboardButton(f"🌸 Аскеза+черновик - {config.ASKEZA_DRAFT_PRICE} руб.", callback_data="subscribe_draft")],
        [InlineKeyboardButton(f"🔮 Аскеза+Нумерология - {config.ASKEZA_NUMEROLOGY_PRICE} руб.", callback_data="subscribe_numerology")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(
            tariffs_text,
            reply_markup=reply_markup
        )
        print(f"✅ [TARIFFS] Тарифы отправлены пользователю {user_id}")
        logger.info(f"[TARIFFS] Тарифы отправлены пользователю {user_id}")
    except Exception as e:
        print(f"❌ [TARIFFS] Ошибка при отправке тарифов пользователю {user_id}: {e}")
        logger.error(f"[TARIFFS] Ошибка при отправке тарифов пользователю {user_id}: {e}")

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
            [InlineKeyboardButton("💎 Тарифы", callback_data="tariffs")],
            [InlineKeyboardButton("📖 Об Аскезе", callback_data="about_askeza")],
            [InlineKeyboardButton("📊 Мой статус", callback_data="my_status")],
            [InlineKeyboardButton("ℹ️ О подписке", callback_data="about_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🏠 Главное меню

Получите доступ к эксклюзивным материалам, закрытым обсуждениям и персональным консультациям.

Нажмите "💎 Тарифы" чтобы выбрать подходящий тариф подписки.
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
    print("🚀 Запуск исправленного бота с подписками...")
    print(f"🌸 Аскеза: {config.ASKEZA_PRICE} рублей")
    print(f"🔮 Аскеза+Нумерология: {config.ASKEZA_NUMEROLOGY_PRICE} рублей")
    print(f"📅 Длительность: {config.SUBSCRIPTION_DAYS} дней")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("📝 Логирование включено")
    
    try:
        # Создаем приложение с правильными настройками
        application = Application.builder().token(config.BOT_TOKEN).build()

        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_tariffs_callback, pattern="tariffs"))
        application.add_handler(CallbackQueryHandler(handle_subscribe_askeza_callback, pattern="subscribe_askeza"))
        application.add_handler(CallbackQueryHandler(handle_subscribe_draft_callback, pattern="subscribe_draft"))
        application.add_handler(CallbackQueryHandler(handle_subscribe_numerology_callback, pattern="subscribe_numerology"))
        application.add_handler(CallbackQueryHandler(handle_check_payment_callback, pattern="check_payment"))
        application.add_handler(CallbackQueryHandler(handle_my_status_callback, pattern="my_status"))
        application.add_handler(CallbackQueryHandler(handle_renew_subscription_callback, pattern="renew_subscription"))
        application.add_handler(CallbackQueryHandler(handle_about_subscription_callback, pattern="about_subscription"))
        application.add_handler(CallbackQueryHandler(handle_about_askeza_callback, pattern="about_askeza"))
        application.add_handler(CallbackQueryHandler(handle_main_menu_callback, pattern="main_menu"))
        application.add_error_handler(error_handler)

        print("✅ Обработчики зарегистрированы:")
        print("   • /start - команда старт")
        print("   • tariffs - отображение тарифов")
        print("   • subscribe_askeza - подписка Аскеза")
        print("   • subscribe_draft - подписка Аскеза+черновик")
        print("   • subscribe_numerology - подписка Аскеза+Нумерология")
        print("   • about_askeza - информация об Аскезе")
        print("   • check_payment - проверка платежа")
        print("   • my_status - статус подписки")
        print("   • renew_subscription - продление подписки")
        print("   • about_subscription - информация о подписке")
        print("   • main_menu - главное меню")
        print("🔍 Тестируйте бота")
        print("📝 Все действия логируются")
        
        # Запускаем бота с правильными параметрами
        print("🚀 Запуск бота...")
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES
        )
        
    except Exception as e:
        print(f"❌ Ошибка при запуске бота: {e}")
        logger.error(f"Ошибка при запуске бота: {e}")
        raise

if __name__ == '__main__':
    main()
