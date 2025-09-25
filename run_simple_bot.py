#!/usr/bin/env python3
"""
Простой запуск бота БЕЗ webhook (упрощенная версия)
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем simple_bot_no_webhook
from simple_bot_no_webhook import main

if __name__ == "__main__":
    print("🚀 Запуск простого бота БЕЗ webhook")
    print("=" * 60)
    print("⚠️ Webhook отключен - платежи проверяются только через API")
    print("🔄 Проверка платежей каждые 5 минут")
    print("📱 Простые уведомления без сложных кнопок")
    print("=" * 60)
    
    main()
