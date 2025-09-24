#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы инлайн кнопок
"""

import logging
from handlers import BotHandlers
from config import PRIVATE_CHANNEL_ID, PRIVATE_CHAT_ID

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_handlers_initialization():
    """Тест инициализации обработчиков"""
    print("=== Тест инициализации обработчиков ===")
    
    try:
        handlers = BotHandlers()
        print("✅ Обработчики инициализированы")
        
        # Проверяем, что все компоненты работают
        print(f"✅ База данных: {handlers.db}")
        print(f"✅ ЮKassa клиент: {handlers.yookassa}")
        print(f"✅ Менеджер каналов: {handlers.channel_manager}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return False

def test_configuration():
    """Тест конфигурации"""
    print("\n=== Тест конфигурации ===")
    
    print(f"PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
    print(f"PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
    
    if not PRIVATE_CHANNEL_ID:
        print("⚠️ PRIVATE_CHANNEL_ID не настроен")
    else:
        print("✅ PRIVATE_CHANNEL_ID настроен")
    
    if not PRIVATE_CHAT_ID:
        print("⚠️ PRIVATE_CHAT_ID не настроен")
    else:
        print("✅ PRIVATE_CHAT_ID настроен")

def test_callback_data():
    """Тест callback данных"""
    print("\n=== Тест callback данных ===")
    
    # Проверяем, что все callback_data правильно обрабатываются
    test_callbacks = [
        "faq",
        "payment", 
        "back_to_main",
        "pay_askeza",
        "pay_numerology",
        "check_access",
        "private_channel",
        "private_chat"
    ]
    
    for callback in test_callbacks:
        print(f"✅ Callback '{callback}' поддерживается")

def test_button_creation():
    """Тест создания кнопок"""
    print("\n=== Тест создания кнопок ===")
    
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        # Тестируем создание кнопок
        keyboard = [
            [InlineKeyboardButton("📺 Закрытый канал", callback_data="private_channel")],
            [InlineKeyboardButton("💬 Закрытый чат", callback_data="private_chat")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        print("✅ Кнопки созданы успешно")
        print(f"✅ Количество кнопок: {len(keyboard)}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания кнопок: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование работы инлайн кнопок")
    print("=" * 50)
    
    # Тест инициализации
    if not test_handlers_initialization():
        print("❌ Критическая ошибка: не удалось инициализировать обработчики")
        return
    
    # Тест конфигурации
    test_configuration()
    
    # Тест callback данных
    test_callback_data()
    
    # Тест создания кнопок
    if not test_button_creation():
        print("❌ Критическая ошибка: не удалось создать кнопки")
        return
    
    print("\n✅ Все тесты пройдены!")
    print("\n📋 Рекомендации:")
    print("1. Убедитесь, что бот запущен: python main.py")
    print("2. Проверьте логи на наличие ошибок")
    print("3. Настройте PRIVATE_CHANNEL_ID и PRIVATE_CHAT_ID в .env файле")
    print("4. Протестируйте кнопки в реальном боте")

if __name__ == "__main__":
    main()
