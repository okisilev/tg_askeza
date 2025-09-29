#!/usr/bin/env python3
"""
Диагностика inline кнопок
"""

import asyncio
import logging
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from config import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="status"))
        application.add_handler(CallbackQueryHandler(lambda u, c: None, pattern="back_to_main"))
        
        # Проверяем количество обработчиков
        handlers = application.handlers[0]
        print(f"✅ Обработчиков зарегистрировано: {len(handlers)}")
        
        for i, handler in enumerate(handlers):
            print(f"   • {i+1}. {type(handler).__name__}: {handler.pattern if hasattr(handler, 'pattern') else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании обработчиков: {e}")
        return False

def test_inline_keyboard():
    """Тест создания inline клавиатуры"""
    print("\n⌨️ Тест создания inline клавиатуры")
    print("=" * 50)
    
    try:
        # Создаем тестовую клавиатуру
        keyboard = [
            [InlineKeyboardButton("💰 Оплатить доступ (299 руб.)", callback_data="pay")],
            [InlineKeyboardButton("🔄 Проверить оплату", callback_data="check_payment")],
            [InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")],
            [InlineKeyboardButton("📊 Статус", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print("✅ Inline клавиатура создана")
        print(f"   • Кнопок: {len(keyboard)}")
        print(f"   • Callback data: pay, check_payment, test_button, status")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при создании inline клавиатуры: {e}")
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

def print_troubleshooting():
    """Печать рекомендаций по устранению неполадок"""
    print("\n" + "=" * 50)
    print("🔧 РЕКОМЕНДАЦИИ ПО УСТРАНЕНИЮ НЕПОЛАДОК")
    print("=" * 50)
    
    print("\n1️⃣ Проверьте, что бот запущен:")
    print("   .venv\\Scripts\\python.exe test_inline_buttons.py")
    
    print("\n2️⃣ Проверьте логи на ошибки:")
    print("   • Ищите ошибки при обработке callback_query")
    print("   • Проверьте ошибки при регистрации обработчиков")
    print("   • Убедитесь, что бот получает обновления")
    
    print("\n3️⃣ Проверьте настройки:")
    print("   • BOT_TOKEN настроен правильно")
    print("   • Бот не заблокирован")
    print("   • Нет конфликтов с другими ботами")
    
    print("\n4️⃣ Перезапустите бота:")
    print("   • Остановите бота (Ctrl+C)")
    print("   • Запустите заново: .venv\\Scripts\\python.exe test_inline_buttons.py")
    
    print("\n5️⃣ Проверьте работу inline кнопок:")
    print("   • Отправьте /start боту")
    print("   • Нажмите на inline кнопки")
    print("   • Проверьте логи на сообщения")
    print("   • Убедитесь, что callback_query обрабатываются")

async def main():
    """Основная функция диагностики"""
    print("🔍 Диагностика inline кнопок")
    print("=" * 50)
    
    # Тестируем все компоненты
    config_ok = test_config()
    bot_ok = await test_bot_connection()
    handlers_ok = test_handlers()
    keyboard_ok = test_inline_keyboard()
    
    print(f"\n📊 Результат диагностики:")
    print(f"   • Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   • Бот: {'✅' if bot_ok else '❌'}")
    print(f"   • Обработчики: {'✅' if handlers_ok else '❌'}")
    print(f"   • Inline клавиатура: {'✅' if keyboard_ok else '❌'}")
    
    if all([config_ok, bot_ok, handlers_ok, keyboard_ok]):
        print("\n🎉 Все компоненты работают!")
        print("Проблема может быть в том, что бот не получает callback_query")
        print("Проверьте работу тестового бота")
    else:
        print("\n⚠️ Есть проблемы с компонентами!")
        print("Проверьте настройки и логи")
    
    # Показываем рекомендации
    print_troubleshooting()

if __name__ == "__main__":
    asyncio.run(main())
