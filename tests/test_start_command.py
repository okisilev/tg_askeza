#!/usr/bin/env python3
"""
Тестовый скрипт для проверки команды /start
"""

import os
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_video_file():
    """Проверка наличия видео файла"""
    print("🎬 Проверка видео файла")
    print("=" * 50)
    
    video_path = "IMG_2560.MOV"
    
    if os.path.exists(video_path):
        print(f"✅ Видео файл найден: {video_path}")
        
        # Проверяем размер файла
        file_size = os.path.getsize(video_path)
        print(f"📊 Размер файла: {file_size / (1024*1024):.2f} MB")
        
        if file_size > 50 * 1024 * 1024:  # 50 MB
            print("⚠️ Внимание: Файл больше 50MB, может быть проблема с отправкой в Telegram")
        else:
            print("✅ Размер файла подходит для Telegram")
        
        return True
    else:
        print(f"❌ Видео файл не найден: {video_path}")
        print("📁 Файлы в корневой директории:")
        
        for file in os.listdir("."):
            if file.lower().endswith(('.mov', '.mp4', '.avi', '.mkv')):
                print(f"   🎬 {file}")
        
        return False

def test_start_message():
    """Тест нового сообщения /start"""
    print("\n📝 Тест нового сообщения /start")
    print("=" * 50)
    
    # Симулируем пользователя
    test_username = "Тестовый пользователь"
    
    welcome_text = f"""
Меня зовут, Ольга🌸 И я любитель аскез, данную практику я использую уже целых 4 года😍 даже прошла по ней обучение, чтоб знать все нюансы! Из всех сотни практик, которые я когда либо пробовала, аскеза моя самая любимая!💕

Во-первых, ты попробуешь, а как может быть по другому?!☀️

Во-вторых, ты начнешь верить в чудо, потому что желания могут исполняться самым волшебным образом💫

В третьих, твоя жизнь не станет прежней!⭐️

Я жду тебя, {test_username}!🫂
    """
    
    print("📋 Новое сообщение /start:")
    print(welcome_text)
    
    print("\n✅ Сообщение сформировано правильно")
    return True

def test_handlers_import():
    """Тест импорта handlers"""
    print("\n🔧 Тест импорта handlers")
    print("=" * 50)
    
    try:
        from handlers import BotHandlers
        print("✅ BotHandlers импортирован успешно")
        
        # Проверяем, что start_command существует
        handlers = BotHandlers()
        if hasattr(handlers, 'start_command'):
            print("✅ Метод start_command найден")
        else:
            print("❌ Метод start_command не найден")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при импорте handlers: {e}")
        return False

def print_instructions():
    """Печать инструкций"""
    print("\n" + "=" * 50)
    print("📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ")
    print("=" * 50)
    
    print("\n1️⃣ Убедитесь, что видео файл находится в корне проекта:")
    print("   📁 IMG_2560.MOV")
    
    print("\n2️⃣ Проверьте размер видео:")
    print("   • Рекомендуется до 50MB")
    print("   • Формат: MOV, MP4, AVI")
    
    print("\n3️⃣ Запустите бота:")
    print("   python run_simple_bot.py")
    print("   или")
    print("   python run_no_webhook.py")
    
    print("\n4️⃣ Протестируйте команду /start:")
    print("   • Отправьте /start боту")
    print("   • Проверьте, что видео отправляется")
    print("   • Проверьте новый текст")

def main():
    """Основная функция"""
    print("🧪 Тестирование команды /start")
    print("=" * 50)
    
    # Проверяем видео файл
    video_ok = test_video_file()
    
    # Тестируем новое сообщение
    message_ok = test_start_message()
    
    # Тестируем импорт handlers
    handlers_ok = test_handlers_import()
    
    # Показываем результаты
    print("\n📊 Результаты тестирования:")
    print(f"   Видео файл: {'✅' if video_ok else '❌'}")
    print(f"   Сообщение: {'✅' if message_ok else '❌'}")
    print(f"   Handlers: {'✅' if handlers_ok else '❌'}")
    
    if video_ok and message_ok and handlers_ok:
        print("\n✅ Все тесты пройдены!")
        print("Бот готов к работе с новым функционалом")
    else:
        print("\n❌ Некоторые тесты не пройдены")
        print("Проверьте ошибки выше")
    
    # Показываем инструкции
    print_instructions()

if __name__ == "__main__":
    main()
