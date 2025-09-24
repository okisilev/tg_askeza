"""
Скрипт для создания файла .env с переменными окружения
"""

import os

def create_env_file():
    """Создание файла .env с примером переменных"""
    env_content = """# Токен бота от @BotFather
BOT_TOKEN=your_bot_token_here

# Настройки ЮKassa
YOOKASSA_SHOP_ID=1163671
YOOKASSA_SECRET_KEY=your_yookassa_secret_key_here

# ID закрытых каналов и чатов (с @)
PRIVATE_CHANNEL_ID=@your_private_channel
PRIVATE_CHAT_ID=@your_private_chat
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("✅ Файл .env создан! Отредактируйте его, указав ваши данные.")
    else:
        print("⚠️ Файл .env уже существует.")

if __name__ == "__main__":
    create_env_file()
