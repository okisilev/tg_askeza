# 🔧 Исправление теста API проверки платежей

## ❌ Проблема
```
❌ Ошибка подключения к ЮKassa: 'YooKassaClient' object has no attribute 'shop_id'
```

## ✅ Решение

### 1️⃣ Исправлен тестовый скрипт

В `test_api_payment_check.py` исправлена функция `test_yookassa_connection()`:

**Старый код (неправильный):**
```python
print(f"   Shop ID: {yookassa_client.shop_id}")  # ❌ Нет такого атрибута
print(f"   Secret Key: {'Настроен' if yookassa_client.secret_key else 'НЕ настроен'}")
```

**Новый код (правильный):**
```python
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY

print(f"   Shop ID: {YOOKASSA_SHOP_ID}")
print(f"   Secret Key: {'Настроен' if YOOKASSA_SECRET_KEY else 'НЕ настроен'}")

# Проверяем конфигурацию ЮKassa
from yookassa import Configuration
if Configuration.account_id and Configuration.secret_key:
    print("✅ Конфигурация ЮKassa установлена")
```

### 2️⃣ Добавлена проверка конфигурации

Новая функция `check_config()` проверяет:
- YOOKASSA_SHOP_ID
- YOOKASSA_SECRET_KEY  
- BOT_TOKEN
- PRIVATE_CHANNEL_ID

### 3️⃣ Добавлен тестовый API запрос

Скрипт теперь:
1. Проверяет настройки
2. Инициализирует YooKassa клиент
3. Проверяет конфигурацию
4. Делает тестовый API запрос
5. Показывает результат

## 🧪 Запуск исправленного теста

```bash
python test_api_payment_check.py
```

### Ожидаемый результат:
```
🧪 Тестирование API проверки платежей
==================================================

🔧 Проверка конфигурации
==================================================
YOOKASSA_SHOP_ID: 1163671
YOOKASSA_SECRET_KEY: Настроен
BOT_TOKEN: Настроен
PRIVATE_CHANNEL_ID: -1002806695160

✅ Все основные настройки заполнены

🔗 Тестирование подключения к ЮKassa API
==================================================
🔍 Проверяем настройки ЮKassa...
   Shop ID: 1163671
   Secret Key: Настроен
✅ YooKassa клиент инициализирован
✅ Конфигурация ЮKassa установлена
🔍 Тестируем API запрос...
✅ API запрос выполнен успешно

✅ Подключение к ЮKassa работает
```

## 🔍 Что проверяет тест

### 1️⃣ Конфигурация:
- Все необходимые переменные окружения
- Правильность настроек ЮKassa
- Наличие токена бота

### 2️⃣ Подключение к ЮKassa:
- Инициализация клиента
- Установка конфигурации
- Тестовый API запрос

### 3️⃣ API проверка платежей:
- Поиск pending платежей в БД
- Проверка статуса через API
- Обновление статусов в БД

## 🚀 После успешного теста

Если тест прошел успешно, можно запускать бота:

```bash
python run_no_webhook.py
```

Или:

```bash
python main_no_webhook.py
```

## 🔧 Если тест все еще не работает

### Проверьте .env файл:
```env
YOOKASSA_SHOP_ID=1163671
YOOKASSA_SECRET_KEY=test_r0kwPnEziXP9IB-oPdBgGbd4VwrdoS5_ejuDtmxmjms
BOT_TOKEN=your_bot_token
PRIVATE_CHANNEL_ID=-1002806695160
```

### Проверьте установку зависимостей:
```bash
pip install yookassa python-telegram-bot python-dotenv
```

### Проверьте права доступа:
- Убедитесь, что файлы доступны для чтения
- Проверьте, что .env файл существует
- Убедитесь, что база данных создана

## 📞 Дополнительная помощь

Если проблемы остаются:

1. **Проверьте логи** на наличие ошибок
2. **Убедитесь в правильности настроек** ЮKassa
3. **Проверьте установку зависимостей**
4. **Убедитесь, что .env файл существует и заполнен**

Теперь тест должен работать правильно!
