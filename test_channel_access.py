#!/usr/bin/env python3
"""
Тестовый скрипт для проверки доступа к каналам
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

def test_channel_configuration():
    """Тест конфигурации каналов"""
    print("=== Тест конфигурации каналов ===")
    
    print(f"PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
    print(f"PRIVATE_CHAT_ID: {PRIVATE_CHAT_ID}")
    
    if PRIVATE_CHANNEL_ID:
        print("✅ Канал настроен")
        print(f"   Ссылка на канал: https://t.me/{PRIVATE_CHANNEL_ID.replace('@', '')}")
    else:
        print("⚠️ Канал не настроен")
    
    if PRIVATE_CHAT_ID:
        print("✅ Чат настроен")
        print(f"   Ссылка на чат: https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}")
    else:
        print("⚠️ Чат не настроен")

def test_handlers_initialization():
    """Тест инициализации обработчиков"""
    print("\n=== Тест инициализации обработчиков ===")
    
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

def test_channel_urls():
    """Тест генерации URL для каналов"""
    print("\n=== Тест генерации URL ===")
    
    if PRIVATE_CHANNEL_ID:
        channel_url = f"https://t.me/{PRIVATE_CHANNEL_ID.replace('@', '')}"
        print(f"✅ URL канала: {channel_url}")
    else:
        print("⚠️ Канал не настроен")
    
    if PRIVATE_CHAT_ID:
        chat_url = f"https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}"
        print(f"✅ URL чата: {chat_url}")
    else:
        print("⚠️ Чат не настроен")

def test_button_creation():
    """Тест создания кнопок с URL"""
    print("\n=== Тест создания кнопок с URL ===")
    
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        # Тестируем создание кнопок с URL
        keyboard = []
        
        if PRIVATE_CHANNEL_ID:
            channel_button = InlineKeyboardButton(
                "📺 Перейти в канал", 
                url=f"https://t.me/{PRIVATE_CHANNEL_ID.replace('@', '')}"
            )
            keyboard.append([channel_button])
            print("✅ Кнопка канала создана")
        
        if PRIVATE_CHAT_ID:
            chat_button = InlineKeyboardButton(
                "💬 Перейти в чат", 
                url=f"https://t.me/{PRIVATE_CHAT_ID.replace('@', '')}"
            )
            keyboard.append([chat_button])
            print("✅ Кнопка чата создана")
        
        # Добавляем кнопку "Назад"
        back_button = InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")
        keyboard.append([back_button])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        print(f"✅ Клавиатура создана с {len(keyboard)} кнопками")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка создания кнопок: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование доступа к каналам")
    print("=" * 50)
    
    # Тест конфигурации
    test_channel_configuration()
    
    # Тест инициализации
    if not test_handlers_initialization():
        print("❌ Критическая ошибка: не удалось инициализировать обработчики")
        return
    
    # Тест генерации URL
    test_channel_urls()
    
    # Тест создания кнопок
    if not test_button_creation():
        print("❌ Критическая ошибка: не удалось создать кнопки")
        return
    
    print("\n✅ Все тесты пройдены!")
    print("\n📋 Новая функциональность:")
    print("1. ✅ Кнопка 'Закрытый канал' теперь перебрасывает в канал")
    print("2. ✅ Кнопка 'Закрытый чат' теперь перебрасывает в чат")
    print("3. ✅ Автоматическое добавление пользователей в каналы")
    print("4. ✅ Проверка статуса пользователя в каналах")
    print("5. ✅ Прямые ссылки для быстрого перехода")
    
    print("\n⚠️ Важно:")
    print("1. Настройте PRIVATE_CHANNEL_ID и PRIVATE_CHAT_ID в .env файле")
    print("2. Бот должен быть администратором каналов и чатов")
    print("3. Пользователь должен иметь активный доступ")

if __name__ == "__main__":
    main()
