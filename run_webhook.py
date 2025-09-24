#!/usr/bin/env python3
"""
Скрипт для запуска webhook сервера
"""

import logging
from webhook_server import app

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Запуск webhook сервера на порту 5000")
    logger.info("📡 Webhook URL: http://localhost:5000/webhook/yookassa")
    logger.info("🏥 Health check: http://localhost:5000/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
