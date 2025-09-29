import os
from dotenv import load_dotenv

load_dotenv()

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
YOOKASSA_SHOP_ID = os.getenv('YOOKASSA_SHOP_ID', '1163671')
YOOKASSA_SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY') or 'test_r0kwPnEziXP9IB-oPdBgGbd4VwrdoS5_ejuDtmxmjms'
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID', '-2073129707770')
PRIVATE_CHAT_ID = os.getenv('PRIVATE_CHAT_ID', '-2073129707770')

# Database
DATABASE_PATH = 'askeza_bot.db'

# Prices (in rubles)
ASKEZA_PRICE = 990  # Цена за доступ к Аскезе
NUMEROLOGY_PRICE = 2490  # Цена за нумерологический разбор

# Access duration (in days)
ACCESS_DURATION = 30
