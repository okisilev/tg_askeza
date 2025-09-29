import logging
import uuid
import asyncio
import threading
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
import yookassa
from yookassa import Payment
from telegram.ext import ApplicationBuilder
from config import config
from database import Database

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация базы данных
db = Database()

# Настройка ЮКассы
yookassa.Configuration.account_id = config.YOOKASSA_SHOP_ID
yookassa.Configuration.secret_key = config.YOOKASSA_SECRET_KEY

class PaymentChecker:
    """Класс для периодической проверки платежей"""
    def __init__(self, application, interval=300):
        self.application = application
        self.interval = interval
        self.is_running = False
        self.thread = None
    
    def start(self):
        """Запуск проверки платежей в отдельном потоке"""
        self.is_running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        logger.info(f"Проверка платежей запущена с интервалом {self.interval} секунд")
    
    def stop(self):
        """Остановка проверки платежей"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        logger.info("Проверка платежей остановлена")
    
    def _run(self):
        """Основной цикл проверки"""
        while self.is_running:
            try:
                # Запускаем проверку в event loop приложения
                asyncio.run_coroutine_threadsafe(
                    self.check_payments(), 
                    self.application.bot._loop
                ).result()
            except Exception as e:
                logger.error(f"Ошибка в проверке платежей: {e}")
            
            time.sleep(self.interval)
    
    async def check_payments(self):
        """Проверка незавершенных платежей"""
        try:
            logger.info("Запуск проверки платежей...")
            
            # Получаем все pending платежи
            with db.connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM payments WHERE status = 'pending' AND created_at > datetime('now', '-1 hour')"
                )
                pending_payments = cursor.fetchall()
            
            for payment in pending_payments:
                try:
                    # Проверяем статус в ЮКассе
                    yoo_payment = Payment.find_one(payment['payment_id'])
                    
                    if yoo_payment.status == 'succeeded':
                        # Обновляем статус в БД
                        db.update_payment_status(payment['payment_id'], 'succeeded')
                        
                        # Отправляем приглашение
                        await self.send_channel_invite(payment['user_id'])
                        
                        logger.info(f"Платеж {payment['payment_id']} подтвержден для пользователя {payment['user_id']}")
                    
                    elif yoo_payment.status in ['canceled', 'failed']:
                        db.update_payment_status(payment['payment_id'], yoo_payment.status)
                        logger.info(f"Платеж {payment['payment_id']} отменен")
                        
                except Exception as e:
                    logger.error(f"Ошибка при проверке платежа {payment['payment_id']}: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка в check_payments: {e}")
    
    async def send_channel_invite(self, user_id: int) -> None:
        """Отправка приглашения в канал"""
        try:
            # Создаем временную ссылку-приглашение
            bot = self.application.bot
            invite_link = await bot.create_chat_invite_link(
                chat_id=config.PRIVATE_CHANNEL_ID,
                member_limit=1,
                creates_join_request=False
            )
            
            # Отправляем приглашение пользователю
            await bot.send_message(
                chat_id=user_id,
                text=f"🎉 Поздравляем с успешной оплатой!\n\n"
                     f"🔗 Ваша ссылка для вступления в канал:\n{invite_link.invite_link}\n\n"
                     f"⚠️ Ссылка действительна для одного использования.",
                disable_web_page_preview=True
            )
            
            logger.info(f"Приглашение отправлено пользователю {user_id}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке приглашения: {e}")

# Глобальная переменная для проверщика платежей
payment_checker = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    user = update.effective_user
    if not user:
        return
    
    db.add_user(user.id, user.username, user.first_name, user.last_name)
    
    keyboard = [
        [InlineKeyboardButton("💰 Купить доступ", callback_data="buy_access")],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"👋 Привет, {user.first_name}!\n\n"
        f"🔒 Этот бот предоставляет доступ к закрытому каналу после оплаты.\n"
        f"💳 Стоимость доступа: {config.PAYMENT_AMOUNT} руб.\n\n"
        f"После успешной оплаты вы получите приглашение в канал автоматически.",
        reply_markup=reply_markup
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "buy_access":
        await create_payment(update, context)
    elif query.data == "help":
        await show_help(update, context)
    elif query.data == "check_payment":
        await check_payment_button(update, context)

async def create_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Создание платежа в ЮКассе"""
    query = update.callback_query
    user = query.from_user
    
    # Проверяем, есть ли активная оплата
    payment_info = db.get_user_payment(user.id)
    if payment_info and payment_info['status'] == 'succeeded':
        await send_channel_invite(user.id, context)
        await query.edit_message_text("✅ У вас уже есть доступ к каналу!")
        return
    
    # Создаем уникальный ID платежа
    payment_id = str(uuid.uuid4())
    
    try:
        # Создаем платеж в ЮКассе
        payment = Payment.create({
            "amount": {
                "value": config.PAYMENT_AMOUNT,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://t.me/{context.bot.username}"
            },
            "capture": True,
            "description": config.PAYMENT_DESCRIPTION,
            "metadata": {
                "user_id": user.id,
                "payment_id": payment_id
            }
        })
        
        # Сохраняем платеж в БД
        db.add_payment(user.id, payment_id, config.PAYMENT_AMOUNT)
        
        # Отправляем ссылку на оплату
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить", url=payment.confirmation.confirmation_url)],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"💳 Оплата доступа к закрытому каналу\n\n"
            f"💰 Сумма: {config.PAYMENT_AMOUNT} руб.\n"
            f"📋 Описание: {config.PAYMENT_DESCRIPTION}\n\n"
            f"После оплаты нажмите кнопку 'Проверить оплату'",
            reply_markup=reply_markup
        )
        
    except Exception as e:
        logger.error(f"Ошибка при создании платежа: {e}")
        await query.edit_message_text("❌ Ошибка при создании платежа. Попробуйте позже.")

async def check_payment_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для проверки оплаты /check"""
    user = update.effective_user
    if not user:
        return
    await check_user_payment(user.id, update, context, is_callback=False)

async def check_payment_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Проверка оплаты по кнопке"""
    query = update.callback_query
    await query.answer()
    user = query.from_user
    await check_user_payment(user.id, query, context, is_callback=True)

async def check_user_payment(user_id: int, update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool) -> None:
    """Общая функция проверки оплаты"""
    try:
        payment_info = db.get_user_payment(user_id)
        
        if not payment_info:
            message = "❌ У вас нет активных платежей."
            if is_callback:
                await update.edit_message_text(message)
            else:
                await update.message.reply_text(message)
            return
        
        if payment_info['status'] == 'succeeded':
            await send_channel_invite(user_id, context)
            message = "✅ Оплата подтверждена! Доступ к каналу предоставлен."
        else:
            # Проверяем статус в ЮКассе
            try:
                payment = Payment.find_one(payment_info['payment_id'])
                if payment.status == 'succeeded':
                    db.update_payment_status(payment_info['payment_id'], 'succeeded')
                    await send_channel_invite(user_id, context)
                    message = "✅ Оплата подтверждена! Доступ к каналу предоставлен."
                else:
                    message = f"⏳ Статус оплаты: {payment.status}\nПопробуйте проверить позже."
            except Exception as e:
                logger.error(f"Ошибка при проверке платежа: {e}")
                message = "❌ Ошибка при проверке платежа. Попробуйте позже."
        
        if is_callback:
            await update.edit_message_text(message)
        else:
            await update.message.reply_text(message)
            
    except Exception as e:
        logger.error(f"Ошибка в check_user_payment: {e}")
        error_msg = "❌ Произошла ошибка. Попробуйте позже."
        if is_callback:
            await update.edit_message_text(error_msg)
        else:
            await update.message.reply_text(error_msg)

async def send_channel_invite(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправка приглашения в канал"""
    try:
        # Создаем временную ссылку-приглашение
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=config.PRIVATE_CHANNEL_ID,
            member_limit=1,
            creates_join_request=False
        )
        
        # Отправляем приглашение пользователю
        await context.bot.send_message(
            chat_id=user_id,
            text=f"🎉 Поздравляем с успешной оплатой!\n\n"
                 f"🔗 Ваша ссылка для вступления в канал:\n{invite_link.invite_link}\n\n"
                 f"⚠️ Ссылка действительна для одного использования.",
            disable_web_page_preview=True
        )
        
        logger.info(f"Приглашение отправлено пользователю {user_id}")
        
    except TelegramError as e:
        logger.error(f"Ошибка Telegram при отправке приглашения: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке приглашения: {e}")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Показ справки"""
    query = update.callback_query
    help_text = """
🤖 **Как это работает:**

1. Нажмите "💰 Купить доступ"
2. Оплатите через безопасную систему ЮКассы
3. После успешной оплаты получите приглашение в канал
4. Перейдите по ссылке и присоединяйтесь к каналу

🔧 **Если возникли проблемы:**
- Нажмите /check для проверки оплаты
- Нажмите кнопку "🔄 Проверить оплату"

💳 **Способы оплаты:** карты, ЮMoney, СБП, Qiwi
"""
    
    await query.edit_message_text(help_text, parse_mode='Markdown')

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Статистика для администратора"""
    user = update.effective_user
    if not user:
        return
    
    # Проверяем, является ли пользователь администратором
    if user.id != 123456789:  # Замените на ваш ID
        await update.message.reply_text("❌ У вас нет прав для просмотра статистики.")
        return
    
    with db.connection() as conn:
        total_payments = conn.execute("SELECT COUNT(*) FROM payments").fetchone()[0]
        successful_payments = conn.execute("SELECT COUNT(*) FROM payments WHERE status = 'succeeded'").fetchone()[0]
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    
    await update.message.reply_text(
        f"📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {total_users}\n"
        f"💳 Всего платежей: {total_payments}\n"
        f"✅ Успешных платежей: {successful_payments}\n"
        f"💰 Выручка: {successful_payments * config.PAYMENT_AMOUNT} руб."
    )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

def main() -> None:
    """Запуск бота"""
    # Создаем приложение
    application = ApplicationBuilder().token(config.BOT_TOKEN).build()
    
    # Запускаем проверку платежей в отдельном потоке
    global payment_checker
    payment_checker = PaymentChecker(application, interval=300)
    payment_checker.start()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_payment_command))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Добавляем обработчики кнопок
    application.add_handler(CallbackQueryHandler(handle_button, pattern="^(buy_access|help|check_payment)$"))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запуск бота
    logger.info("Бот запущен...")
    
    try:
        application.run_polling()
    except KeyboardInterrupt:
        logger.info("Бот останавливается...")
    finally:
        if payment_checker:
            payment_checker.stop()

if __name__ == "__main__":
    main()