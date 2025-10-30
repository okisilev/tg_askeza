#!/usr/bin/env python3
"""
Конфигурация бота для подписки на приватный канал
"""

import os
from dataclasses import dataclass
from datetime import timedelta

# Получаем путь к директории, где находится этот скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

@dataclass
class Config:
    # Токен бота от @BotFather
    BOT_TOKEN: str = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"
    
    # Ключи ЮКассы
    YOOKASSA_SHOP_ID: str = "1163671"
    YOOKASSA_SECRET_KEY: str = "live_gglRueTPx8YLNJ4h2p36zsS-YwnZm4rpql5TY0QCmJM"
    
    # ID приватного канала
    PRIVATE_CHANNEL_ID: str = "-1003129707770"
    
    # Постоянная ссылка-приглашение в группу/чат (используется ботом для выдачи доступа)
    GROUP_INVITE_LINK: str = "https://t.me/+-Qw-jcbmVWU0ZjAy"
    
    # ID администратора для уведомлений
    ADMIN_ID: int = 431292182  # Замените на ваш Telegram ID
    
    # Настройки подписки
    SUBSCRIPTION_DAYS: int = 30  # Длительность подписки в днях
    WARNING_DAYS: int = 3  # За сколько дней предупреждать об окончании
    
    # Цены и описания подписок
    ASKEZA_PRICE: float = 990.0  # Цена базовой подписки "Аскеза"
    ASKEZA_NUMEROLOGY_PRICE: float = 2490.0  # Цена расширенной подписки "Аскеза+Нумерология"
    ASKEZA_DRAFT_PRICE: float = 1323.0  # Цена подписки "Аскеза+черновик"
    
    ASKEZA_DESCRIPTION: str = "Аскеза - доступ к закрытому каналу на 30 дней"
    ASKEZA_NUMEROLOGY_DESCRIPTION: str = "Аскеза+Нумерологический разбор - расширенный доступ на 30 дней"
    ASKEZA_DRAFT_DESCRIPTION: str = "Аскеза+черновик - расширенный доступ на 30 дней"
    
    # Настройки базы данных (абсолютный путь)
    DATABASE_PATH: str = os.path.join(SCRIPT_DIR, "subscription_bot.db")
    
    # Настройки уведомлений
    NOTIFICATION_HOUR: int = 12  # Час отправки уведомлений (12:00)
    
    # Тексты сообщений
    WELCOME_MESSAGE: str = """
🌸 Добро пожаловать в Аскезу!

Получите доступ к эксклюзивным материалам и закрытым обсуждениям.

Подписка на 30 дней за {price} рублей.
    """
    
    SUBSCRIPTION_EXPIRED_MESSAGE: str = """
⚠️ Ваша подписка истекла!

Для продолжения доступа к приватному каналу необходимо продлить подписку.
    """
    
    SUBSCRIPTION_EXPIRING_MESSAGE: str = """
⏰ Ваша подписка истекает через {days} дней!

Продлите подписку, чтобы не потерять доступ к эксклюзивным материалам.
    """

config = Config()
