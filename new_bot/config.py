import os
from dataclasses import dataclass

@dataclass
class Config:
    # Токен бота от @BotFather
    BOT_TOKEN: str = "7843200583:AAF-CcQg5zsSe3jfR5_jbAJ8L8ggtKTzGDw"
    
    # Ключи ЮКассы
    YOOKASSA_SHOP_ID: str = "1163671"
    YOOKASSA_SECRET_KEY: str = "test_r0kwPnEziXP9IB-oPdBgGbd4VwrdoS5_ejuDtmxmjms"
    
    # ID закрытого канала
    PRIVATE_CHANNEL_ID: str = "-2073129707770"
    
    # Сумма оплаты (в рублях)
    PAYMENT_AMOUNT: float = 299.0
    PAYMENT_DESCRIPTION: str = "Доступ к закрытому каналу"
    
    # Настройки базы данных
    DATABASE_URL: str = "sqlite:///payments.db"

config = Config()