#!/usr/bin/env python3
"""
Конфигурация бота для подписки на приватный канал
"""

import os
from dataclasses import dataclass
from datetime import timedelta

@dataclass
class Config:
    # Токен бота от @BotFather
    BOT_TOKEN: str = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"
    
    # Ключи ЮКассы
    YOOKASSA_SHOP_ID: str = "1163671"
    YOOKASSA_SECRET_KEY: str = "test_r0kwPnEziXP9IB-oPdBgGbd4VwrdoS5_ejuDtmxmjms"
    
    # ID приватного канала
    PRIVATE_CHANNEL_ID: str = "-2073129707770"
    
    # Настройки подписки
    SUBSCRIPTION_PRICE: float = 299.0  # Цена подписки в рублях
    SUBSCRIPTION_DAYS: int = 30  # Длительность подписки в днях
    WARNING_DAYS: int = 3  # За сколько дней предупреждать об окончании
    
    # Описание платежа
    PAYMENT_DESCRIPTION: str = "Подписка на приватный канал на 30 дней"
    
    # Настройки базы данных
    DATABASE_PATH: str = "subscription_bot.db"
    
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
