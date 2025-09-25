#!/usr/bin/env python3
"""
Простой запуск бота БЕЗ webhook (только API проверка платежей)
"""

import sys
import os

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем main_no_webhook
from main_no_webhook import main

if __name__ == "__main__":
    print("🚀 Запуск бота БЕЗ webhook (только API проверка платежей)")
    print("=" * 60)
    print("⚠️ Webhook отключен - платежи проверяются только через API")
    print("🔄 Проверка платежей каждые 5 минут")
    print("=" * 60)
    
    main()
