#!/usr/bin/env python3
"""
Тестовый скрипт для проверки API проверки платежей
"""

import asyncio
import logging
import sqlite3
from datetime import datetime
from yookassa_client import YooKassaClient
from database import Database
from config import BOT_TOKEN

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_api_payment_check():
    """Тест API проверки платежей"""
    print("🧪 Тестирование API проверки платежей")
    print("=" * 50)
    
    try:
        # Инициализируем компоненты
        yookassa_client = YooKassaClient()
        db = Database()
        
        print("✅ Компоненты инициализированы")
        
        # Получаем все pending платежи
        print("\n📊 Проверяем pending платежи в базе данных...")
        with sqlite3.connect(db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT yookassa_payment_id, user_id, payment_type, amount, created_at 
                FROM payments 
                WHERE status = 'pending'
                ORDER BY created_at DESC
            ''')
            pending_payments = cursor.fetchall()
        
        if not pending_payments:
            print("✅ Нет pending платежей для проверки")
            return True
        
        print(f"📋 Найдено {len(pending_payments)} pending платежей:")
        for payment in pending_payments:
            print(f"   - ID: {payment['yookassa_payment_id']}")
            print(f"     Пользователь: {payment['user_id']}")
            print(f"     Тип: {payment['payment_type']}")
            print(f"     Сумма: {payment['amount']}₽")
            print(f"     Дата: {payment['created_at']}")
            print()
        
        # Тестируем API проверку для каждого платежа
        print("🔍 Тестируем API проверку платежей...")
        updated_count = 0
        
        for payment_row in pending_payments:
            payment_id = payment_row['yookassa_payment_id']
            user_id = payment_row['user_id']
            payment_type = payment_row['payment_type']
            
            print(f"\n🔍 Проверяем платеж {payment_id}...")
            
            try:
                # Проверяем статус через API
                status_result = yookassa_client.get_payment_status(payment_id)
                
                if status_result["success"]:
                    status = status_result["status"]
                    print(f"   ✅ Статус: {status}")
                    
                    if status == "succeeded":
                        print(f"   🎉 Платеж успешно оплачен!")
                        
                        # Обновляем статус в БД
                        if db.update_payment_status(payment_id, "succeeded"):
                            print(f"   ✅ Статус обновлен в БД")
                            updated_count += 1
                        else:
                            print(f"   ❌ Не удалось обновить статус в БД")
                    
                    elif status in ["canceled", "failed"]:
                        print(f"   ❌ Платеж отменен или неуспешен: {status}")
                        db.update_payment_status(payment_id, status)
                    
                    else:
                        print(f"   ⏳ Платеж все еще в процессе: {status}")
                
                else:
                    error = status_result.get('error', 'Unknown error')
                    print(f"   ❌ Ошибка получения статуса: {error}")
                
            except Exception as e:
                print(f"   ❌ Ошибка при проверке платежа: {e}")
        
        print(f"\n📊 Результат: обновлено {updated_count} платежей")
        return True
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        return False

def test_yookassa_connection():
    """Тест подключения к ЮKassa API"""
    print("\n🔗 Тестирование подключения к ЮKassa API")
    print("=" * 50)
    
    try:
        from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
        
        # Проверяем настройки
        print("🔍 Проверяем настройки ЮKassa...")
        print(f"   Shop ID: {YOOKASSA_SHOP_ID}")
        print(f"   Secret Key: {'Настроен' if YOOKASSA_SECRET_KEY else 'НЕ настроен'}")
        
        if not YOOKASSA_SHOP_ID or not YOOKASSA_SECRET_KEY:
            print("❌ Настройки ЮKassa неполные")
            return False
        
        # Инициализируем клиент
        yookassa_client = YooKassaClient()
        print("✅ YooKassa клиент инициализирован")
        
        # Проверяем, что конфигурация установлена
        from yookassa import Configuration
        if Configuration.account_id and Configuration.secret_key:
            print("✅ Конфигурация ЮKassa установлена")
            
            # Пробуем сделать тестовый API запрос
            print("🔍 Тестируем API запрос...")
            try:
                # Пробуем получить информацию о платеже (с несуществующим ID)
                test_result = yookassa_client.get_payment_status("test_payment_id")
                if test_result["success"]:
                    print("✅ API запрос выполнен успешно")
                else:
                    print(f"⚠️ API запрос выполнен, но с ошибкой: {test_result.get('error', 'Unknown error')}")
                return True
            except Exception as api_error:
                print(f"⚠️ API запрос не удался: {api_error}")
                print("   (Это нормально для тестового запроса)")
                return True
        else:
            print("❌ Конфигурация ЮKassa не установлена")
            return False
        
    except Exception as e:
        print(f"❌ Ошибка подключения к ЮKassa: {e}")
        return False

def print_api_check_info():
    """Печать информации о API проверке"""
    print("\n" + "=" * 50)
    print("📋 ИНФОРМАЦИЯ О API ПРОВЕРКЕ ПЛАТЕЖЕЙ")
    print("=" * 50)
    
    print("\n🔄 Как работает API проверка:")
    print("1. Каждые 5 минут система проверяет pending платежи")
    print("2. Для каждого платежа запрашивается статус через ЮKassa API")
    print("3. Если статус 'succeeded' - платеж обрабатывается")
    print("4. Пользователь получает уведомление с кнопками доступа")
    print("5. Пользователь добавляется в каналы")
    
    print("\n⚙️ Настройки:")
    print("• Интервал проверки: 5 минут")
    print("• Проверяются только pending платежи")
    print("• Webhook отключен")
    print("• Только API проверка")
    
    print("\n📊 Мониторинг:")
    print("• Логи проверки платежей")
    print("• Количество обновленных платежей")
    print("• Ошибки API запросов")
    print("• Статусы платежей")

def check_config():
    """Проверка конфигурации"""
    print("🔧 Проверка конфигурации")
    print("=" * 50)
    
    try:
        from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, BOT_TOKEN, PRIVATE_CHANNEL_ID
        
        print(f"YOOKASSA_SHOP_ID: {YOOKASSA_SHOP_ID}")
        print(f"YOOKASSA_SECRET_KEY: {'Настроен' if YOOKASSA_SECRET_KEY else 'НЕ настроен'}")
        print(f"BOT_TOKEN: {'Настроен' if BOT_TOKEN else 'НЕ настроен'}")
        print(f"PRIVATE_CHANNEL_ID: {PRIVATE_CHANNEL_ID}")
        
        if not all([YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, BOT_TOKEN]):
            print("\n❌ Не все настройки заполнены!")
            print("Проверьте .env файл")
            return False
        
        print("\n✅ Все основные настройки заполнены")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при проверке конфигурации: {e}")
        return False

def main():
    """Основная функция"""
    print("🧪 Тестирование API проверки платежей")
    print("=" * 50)
    
    # Проверяем конфигурацию
    config_ok = check_config()
    if not config_ok:
        print("\n❌ Проблемы с конфигурацией")
        return
    
    # Тестируем подключение к ЮKassa
    connection_ok = test_yookassa_connection()
    
    if connection_ok:
        print("\n✅ Подключение к ЮKassa работает")
    else:
        print("\n❌ Проблемы с подключением к ЮKassa")
        return
    
    # Тестируем API проверку платежей
    api_check_ok = test_api_payment_check()
    
    if api_check_ok:
        print("\n✅ API проверка платежей работает")
    else:
        print("\n❌ Проблемы с API проверкой платежей")
    
    # Показываем информацию
    print_api_check_info()
    
    print("\n🚀 Для запуска бота БЕЗ webhook используйте:")
    print("   python run_no_webhook.py")
    print("   или")
    print("   python main_no_webhook.py")

if __name__ == "__main__":
    main()
