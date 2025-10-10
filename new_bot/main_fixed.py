#!/usr/bin/env python3
"""
Основной файл для запуска исправленного бота с планировщиком уведомлений
"""

import asyncio
import threading
import time
import logging
import os
import sys
from bot_fixed import main as bot_main
from scheduler import NotificationScheduler
from config import config

# Устанавливаем рабочую директорию на директорию скрипта
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
print(f"📁 Рабочая директория установлена: {SCRIPT_DIR}")

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def run_bot():
    """Запуск исправленного бота в отдельном потоке"""
    print("🤖 Запуск исправленного Telegram бота...")
    try:
        # Создаем новый event loop для этого потока
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем исправленного бота
        bot_main()
    except Exception as e:
        print(f"❌ Ошибка в боте: {e}")
        logger.error(f"Ошибка в боте: {e}")
        # Не прерываем выполнение, планировщик продолжает работать

def run_scheduler():
    """Запуск планировщика уведомлений"""
    print("📅 Запуск планировщика уведомлений...")
    scheduler = NotificationScheduler()
    
    try:
        scheduler.start()
        
        # Показываем время следующего запуска
        next_run = scheduler.get_next_run_time()
        if next_run:
            print(f"⏰ Следующая проверка уведомлений: {next_run}")
        
        # Ждем сигнала остановки
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки планировщика...")
        scheduler.stop()
    except Exception as e:
        print(f"❌ Ошибка в планировщике: {e}")
        logger.error(f"Ошибка в планировщике: {e}")

def main():
    """Основная функция запуска"""
    print("🚀 Запуск системы исправленного бота с подписками")
    print("=" * 50)
    print(f"🌸 Аскеза: {config.ASKEZA_PRICE} рублей")
    print(f"🔮 Аскеза+Нумерология: {config.ASKEZA_NUMEROLOGY_PRICE} рублей")
    print(f"📅 Длительность: {config.SUBSCRIPTION_DAYS} дней")
    print(f"⏰ Уведомления: {config.NOTIFICATION_HOUR}:00")
    print(f"📺 Канал: {config.PRIVATE_CHANNEL_ID}")
    print("=" * 50)
    
    # Запускаем исправленного бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Небольшая задержка для инициализации бота
    time.sleep(3)
    
    # Запускаем планировщик в основном потоке
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n🛑 Получен сигнал остановки...")
        print("✅ Система остановлена")

if __name__ == "__main__":
    main()
