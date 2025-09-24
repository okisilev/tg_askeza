#!/usr/bin/env python3
"""
Скрипт для запуска интегрированного бота
"""

import logging
from integrated_bot import IntegratedBot, start_webhook_server, periodic_payment_check
import threading

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Запуск интегрированной программы")
    
    # Запускаем периодическую проверку платежей в отдельном потоке
    payment_check_thread = threading.Thread(target=periodic_payment_check, daemon=True)
    payment_check_thread.start()
    logger.info("✅ Запущена периодическая проверка платежей")
    
    # Запускаем webhook сервер в отдельном потоке
    webhook_thread = threading.Thread(target=start_webhook_server, daemon=True)
    webhook_thread.start()
    logger.info("✅ Запущен webhook сервер")
    
    # Запускаем интегрированный бот в основном потоке
    integrated_bot = IntegratedBot()
    integrated_bot.run()
