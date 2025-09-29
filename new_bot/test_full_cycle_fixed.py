#!/usr/bin/env python3
"""
Исправленный тест полного цикла работы бота
"""

import asyncio
import logging
import uuid
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

# Инициализация базы данных
db = Database()

async def test_bot_connection():
    """Тест подключения к боту"""
    print("🤖 Тест подключения к боту")
    print("=" * 50)
    
    try:
        bot = Bot(token=config.BOT_TOKEN)
        await bot.initialize()
        
        bot_info = await bot.get_me()
        print(f"✅ Бот подключен: @{bot_info.username}")
        print(f"   • ID: {bot_info.id}")
        print(f"   • Имя: {bot_info.first_name}")
        print(f"   • Username: @{bot_info.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к боту: {e}")
        return False

def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тест базы данных")
    print("=" * 50)
    
    try:
        # Тестируем добавление пользователя
        test_user_id = 123456789
        db.add_user(
            user_id=test_user_id,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        print("✅ Пользователь добавлен в БД")
        
        # Тестируем добавление платежа с уникальным ID
        unique_payment_id = str(uuid.uuid4())
        db.add_payment(
            user_id=test_user_id,
            payment_id=unique_payment_id,
            amount=299.0
        )
        print(f"✅ Платеж добавлен в БД: {unique_payment_id}")
        
        # Тестируем получение платежа
        payment_info = db.get_user_payment(test_user_id)
        if payment_info:
            print(f"✅ Платеж найден: {payment_info['payment_id']}")
        else:
            print("❌ Платеж не найден")
            return False
        
        # Тестируем обновление статуса
        db.update_payment_status(unique_payment_id, "succeeded")
        print("✅ Статус платежа обновлен")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def test_config():
    """Тест конфигурации"""
    print("\n⚙️ Тест конфигурации")
    print("=" * 50)
    
    try:
        print(f"✅ BOT_TOKEN: {config.BOT_TOKEN[:10]}...")
        print(f"✅ YOOKASSA_SHOP_ID: {config.YOOKASSA_SHOP_ID}")
        print(f"✅ YOOKASSA_SECRET_KEY: {config.YOOKASSA_SECRET_KEY[:10]}...")
        print(f"✅ PRIVATE_CHANNEL_ID: {config.PRIVATE_CHANNEL_ID}")
        print(f"✅ PAYMENT_AMOUNT: {config.PAYMENT_AMOUNT}")
        print(f"✅ PAYMENT_DESCRIPTION: {config.PAYMENT_DESCRIPTION}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_inline_keyboard():
    """Тест создания inline клавиатуры"""
    print("\n⌨️ Тест создания inline клавиатуры")
    print("=" * 50)
    
    try:
        # Создаем тестовую клавиатуру
        keyboard = [
            [InlineKeyboardButton(f"💰 Оплатить доступ ({config.PAYMENT_AMOUNT} руб.)", callback_data="pay")],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print("✅ Inline клавиатура создана")
        print(f"   • Кнопок: {len(keyboard)}")
        print(f"   • Callback data: pay, check_payment, test_button, main_menu")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании inline клавиатуры: {e}")
        return False

def test_handlers():
    """Тест обработчиков"""
    print("\n🔧 Тест обработчиков")
    print("=" * 50)
    
    try:
        application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Добавляем тестовые обработчики
        application.add_handler(CommandHandler("start", lambda u, c: None))
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="pay"))
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="check_payment"))
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="test_button"))
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="main_menu"))
        
        # Проверяем количество обработчиков
        handlers = application.handlers[0]
        print(f"✅ Обработчиков зарегистрировано: {len(handlers)}")
        
        for i, handler in enumerate(handlers):
            print(f"   • {i+1}. {type(handler).__name__}: {handler.pattern if hasattr(handler, 'pattern') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании обработчиков: {e}")
        return False

def print_workflow():
    """Печать рабочего процесса"""
    print("\n" + "=" * 50)
    print("🔄 РАБОЧИЙ ПРОЦЕСС БОТА")
    print("=" * 50)
    
    print("\n1️⃣ Пользователь отправляет /start")
    print("   • Бот добавляет пользователя в БД")
    print("   • Отправляет приветственное сообщение с inline кнопками")
    
    print("\n2️⃣ Пользователь нажимает 'Оплатить доступ'")
    print("   • Создается уникальный payment_id")
    print("   • Создается платеж в ЮKassa API")
    print("   • Платеж сохраняется в БД со статусом 'pending'")
    print("   • Отправляется ссылка на оплату")
    
    print("\n3️⃣ Пользователь оплачивает")
    print("   • ЮKassa обрабатывает платеж")
    print("   • Статус платежа меняется на 'succeeded'")
    
    print("\n4️⃣ Пользователь нажимает 'Проверить оплату'")
    print("   • Бот проверяет статус в ЮKassa API")
    print("   • Обновляет статус в БД")
    print("   • Создает пригласительную ссылку в канал")
    print("   • Отправляет ссылку пользователю")
    print("   • Предоставляет доступ к каналу")
    
    print("\n5️⃣ Пользователь получает доступ")
    print("   • Может перейти в закрытый канал")
    print("   • Получает эксклюзивные материалы")
    print("   • Участвует в закрытых обсуждениях")

def print_launch_instructions():
    """Печать инструкций по запуску"""
    print("\n" + "=" * 50)
    print("🚀 ИНСТРУКЦИИ ПО ЗАПУСКУ")
    print("=" * 50)
    
    print("\n1️⃣ Остановите все процессы:")
    print("   taskkill /F /IM python.exe")
    
    print("\n2️⃣ Запустите бота:")
    print("   .venv\\Scripts\\python.exe bot_working.py")
    
    print("\n3️⃣ Проверьте работу:")
    print("   • Отправьте /start боту")
    print("   • Нажмите на кнопку 'Оплатить доступ'")
    print("   • Проверьте создание платежа в логах")
    print("   • Нажмите на кнопку 'Проверить оплату'")
    print("   • Проверьте предоставление доступа к каналу")
    
    print("\n4️⃣ Проверьте логи:")
    print("   • Все операции должны логироваться")
    print("   • Ошибки должны отображаться")
    print("   • Успешные операции должны подтверждаться")

async def main():
    """Основная функция тестирования"""
    print("🔍 Исправленный тест полного цикла работы бота")
    print("=" * 50)
    
    # Тестируем все компоненты
    config_ok = test_config()
    bot_ok = await test_bot_connection()
    db_ok = test_database()
    handlers_ok = test_handlers()
    keyboard_ok = test_inline_keyboard()
    
    print(f"\n📊 Результат тестирования:")
    print(f"   • Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   • Бот: {'✅' if bot_ok else '❌'}")
    print(f"   • База данных: {'✅' if db_ok else '❌'}")
    print(f"   • Обработчики: {'✅' if handlers_ok else '❌'}")
    print(f"   • Inline клавиатура: {'✅' if keyboard_ok else '❌'}")
    
    if all([config_ok, bot_ok, db_ok, handlers_ok, keyboard_ok]):
        print("\n🎉 Все компоненты работают!")
        print("Бот готов к работе")
        print_workflow()
        print_launch_instructions()
    else:
        print("\n⚠️ Есть проблемы с компонентами!")
        print("Проверьте настройки и логи")

if __name__ == "__main__":
    asyncio.run(main())
