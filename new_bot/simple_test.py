#!/usr/bin/env python3
"""
Простой тест конфигурации
"""

def test_config():
    """Тест конфигурации"""
    print("🔍 Тест конфигурации")
    print("=" * 50)
    
    try:
        from config import config
        
        print(f"✅ BOT_TOKEN: {config.BOT_TOKEN[:10]}...")
        print(f"✅ YOOKASSA_SHOP_ID: {config.YOOKASSA_SHOP_ID}")
        print(f"✅ YOOKASSA_SECRET_KEY: {config.YOOKASSA_SECRET_KEY[:10]}...")
        print(f"✅ PRIVATE_CHANNEL_ID: {config.PRIVATE_CHANNEL_ID}")
        print(f"✅ SUBSCRIPTION_PRICE: {config.SUBSCRIPTION_PRICE}")
        print(f"✅ SUBSCRIPTION_DAYS: {config.SUBSCRIPTION_DAYS}")
        print(f"✅ WARNING_DAYS: {config.WARNING_DAYS}")
        print(f"✅ NOTIFICATION_HOUR: {config.NOTIFICATION_HOUR}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_database():
    """Тест базы данных"""
    print("\n🗄️ Тест базы данных")
    print("=" * 50)
    
    try:
        from database import Database
        
        db = Database()
        print("✅ База данных инициализирована")
        
        # Тестируем добавление пользователя
        test_user_id = 123456789
        db.add_user(
            user_id=test_user_id,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        print("✅ Пользователь добавлен в БД")
        
        # Тестируем создание подписки
        db.create_subscription(
            user_id=test_user_id,
            payment_id="test_payment_123",
            amount=299.0
        )
        print("✅ Подписка создана в БД")
        
        # Тестируем проверку активности подписки
        is_active = db.is_subscription_active(test_user_id)
        print(f"✅ Подписка активна: {is_active}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка базы данных: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🔍 Простой тест системы")
    print("=" * 50)
    
    # Тестируем все компоненты
    config_ok = test_config()
    db_ok = test_database()
    
    print(f"\n📊 Результат тестирования:")
    print(f"   • Конфигурация: {'✅' if config_ok else '❌'}")
    print(f"   • База данных: {'✅' if db_ok else '❌'}")
    
    if all([config_ok, db_ok]):
        print("\n🎉 Все компоненты работают!")
        print("Система готова к работе")
    else:
        print("\n⚠️ Есть проблемы с компонентами!")
        print("Проверьте настройки и логи")

if __name__ == "__main__":
    main()
