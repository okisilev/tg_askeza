#!/usr/bin/env python3
"""
Упрощенный запуск основной программы
"""

import logging
from main import start_bot, start_webhook_server, periodic_payment_check
import threading
import time

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Запуск основной программы")
    
    # Запускаем периодическую проверку платежей в отдельном потоке
    payment_check_thread = threading.Thread(target=periodic_payment_check, daemon=True)
    payment_check_thread.start()
    logger.info("✅ Запущена периодическая проверка платежей")
    
    # Запускаем webhook сервер в отдельном потоке
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()
    logger.info("✅ Запущен webhook сервер")
    
    # Запускаем бота в основном потоке
    start_bot()
