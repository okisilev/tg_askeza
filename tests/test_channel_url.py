#!/usr/bin/env python3
"""
Тестовый скрипт для проверки формирования ссылки на канал
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def get_channel_url(channel_id):
    """Получение правильной ссылки на канал"""
    if not channel_id:
        return None
    
    if channel_id.startswith('@'):
        # Для каналов с @username
        return f"https://t.me/{channel_id.replace('@', '')}"
    else:
        # Для числовых ID каналов (например, -1002806695160)
        # Убираем -100 и используем оставшуюся часть
        if channel_id.startswith('-100'):
            channel_id_clean = channel_id[4:]
        else:
            channel_id_clean = channel_id
        return f"https://t.me/c/{channel_id_clean}"

def test_channel_urls():
    """Тест формирования ссылок на каналы"""
    print("🔗 Тестирование формирования ссылок на каналы")
    print("=" * 50)
    
    # Тестируем разные форматы ID каналов
    test_cases = [
        ("@test_channel", "Канал с @username"),
        ("-1002806695160", "Числовой ID канала"),
        ("-1001234567890", "Другой числовой ID"),
        ("@askeza_channel", "Канал Аскезы с @username"),
    ]
    
    for channel_id, description in test_cases:
        url = get_channel_url(channel_id)
        print(f"\n📺 {description}:")
        print(f"   ID: {channel_id}")
        print(f"   URL: {url}")
    
    # Проверяем текущую настройку
    print(f"\n🔧 Текущая настройка:")
    private_channel_id = os.getenv('PRIVATE_CHANNEL_ID')
    print(f"   PRIVATE_CHANNEL_ID: {private_channel_id}")
    
    if private_channel_id:
        current_url = get_channel_url(private_channel_id)
        print(f"   Сформированная ссылка: {current_url}")
        
        # Проверяем, является ли это правильной ссылкой
        if private_channel_id.startswith('-100'):
            print(f"   ✅ Числовой ID канала обработан правильно")
            print(f"   📝 Для канала {private_channel_id} будет использована ссылка: {current_url}")
        elif private_channel_id.startswith('@'):
            print(f"   ✅ Username канала обработан правильно")
        else:
            print(f"   ⚠️ Неизвестный формат ID канала")
    else:
        print(f"   ❌ PRIVATE_CHANNEL_ID не настроен")

def print_instructions():
    """Печать инструкций по настройке"""
    print("\n" + "=" * 50)
    print("📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ КАНАЛА")
    print("=" * 50)
    
    print("\n1️⃣ Для каналов с @username:")
    print("   PRIVATE_CHANNEL_ID=@your_channel_name")
    print("   Ссылка будет: https://t.me/your_channel_name")
    
    print("\n2️⃣ Для каналов с числовым ID:")
    print("   PRIVATE_CHANNEL_ID=-1002806695160")
    print("   Ссылка будет: https://t.me/c/2806695160")
    
    print("\n3️⃣ Как получить ID канала:")
    print("   • Добавьте бота в канал как администратора")
    print("   • Отправьте сообщение в канал")
    print("   • Перейдите: https://api.telegram.org/bot<BOT_TOKEN>/getUpdates")
    print("   • Найдите 'chat':{'id':-1002806695160}")
    
    print("\n4️⃣ Проверка настроек:")
    print("   • Убедитесь, что бот является администратором канала")
    print("   • Проверьте права бота на приглашение пользователей")
    print("   • Запустите бота и протестируйте кнопку 'Закрытый канал'")

def main():
    """Основная функция"""
    print("🤖 Тестирование ссылок на каналы")
    print("=" * 50)
    
    # Тестируем формирование ссылок
    test_channel_urls()
    
    # Показываем инструкции
    print_instructions()
    
    print("\n✅ Тест завершен!")
    print("Теперь бот должен правильно формировать ссылки на канал")

if __name__ == "__main__":
    main()
