#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота
"""

import logging
from bot import AskezaBot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🤖 Запуск Telegram бота Аскезы")
    
    try:
        bot = AskezaBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
