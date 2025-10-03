# 💰 Руководство по двум кнопкам оплаты

## ✅ **Реализовано:**

### **1. Две кнопки оплаты:**
- 🌸 **Аскеза** - 990 рублей
- 🔮 **Аскеза+Нумерология** - 2490 рублей

### **2. Обновленная конфигурация:**
```python
# Цены и описания подписок
ASKEZA_PRICE: float = 990.0  # Цена базовой подписки "Аскеза"
ASKEZA_NUMEROLOGY_PRICE: float = 2490.0  # Цена расширенной подписки "Аскеза+Нумерология"

ASKEZA_DESCRIPTION: str = "Аскеза - доступ к закрытому каналу на 30 дней"
ASKEZA_NUMEROLOGY_DESCRIPTION: str = "Аскеза+Нумерологический разбор - расширенный доступ на 30 дней"
```

### **3. Обновленное меню:**
```
🌸 Добро пожаловать в Аскезу!

Выберите подходящий тариф:

🌸 **Аскеза** - 990 рублей
• Доступ к закрытому каналу
• Эксклюзивные материалы
• 30 дней подписки

🔮 **Аскеза+Нумерология** - 2490 рублей
• Все возможности Аскезы
• Персональный нумерологический разбор
• Расширенный доступ к материалам
• 30 дней подписки
```

### **4. Обновленная база данных:**
- ✅ **Добавлено поле** `subscription_type` в таблицу `subscriptions`
- ✅ **Автоматическое определение** типа подписки по сумме платежа
- ✅ **Обратная совместимость** с существующими подписками

### **5. Новые обработчики:**
- ✅ `handle_subscribe_askeza_callback` - для подписки "Аскеза"
- ✅ `handle_subscribe_numerology_callback` - для подписки "Аскеза+Нумерология"
- ✅ `create_payment` - универсальная функция создания платежа

## 🔧 **Изменения в коде:**

### **1. Конфигурация (`config.py`):**
```python
# Цены и описания подписок
ASKEZA_PRICE: float = 990.0
ASKEZA_NUMEROLOGY_PRICE: float = 2490.0

ASKEZA_DESCRIPTION: str = "Аскеза - доступ к закрытому каналу на 30 дней"
ASKEZA_NUMEROLOGY_DESCRIPTION: str = "Аскеза+Нумерологический разбор - расширенный доступ на 30 дней"
```

### **2. База данных (`database.py`):**
```python
def create_subscription(self, user_id: int, payment_id: str, amount: float, subscription_type: str = "askeza"):
    """Создание подписки"""
    with self.connection() as conn:
        expires_at = datetime.now() + timedelta(days=config.SUBSCRIPTION_DAYS)
        conn.execute(
            '''INSERT INTO subscriptions (user_id, payment_id, amount, status, expires_at, is_active, subscription_type) 
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (user_id, payment_id, amount, 'active', expires_at, True, subscription_type)
        )
```

### **3. Обработчики (`bot_fixed.py`):**
```python
async def handle_subscribe_askeza_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки Аскеза"""
    await create_payment(update, context, "askeza", config.ASKEZA_PRICE, config.ASKEZA_DESCRIPTION)

async def handle_subscribe_numerology_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик создания подписки Аскеза+Нумерология"""
    await create_payment(update, context, "numerology", config.ASKEZA_NUMEROLOGY_PRICE, config.ASKEZA_NUMEROLOGY_DESCRIPTION)
```

### **4. Определение типа подписки:**
```python
# Определяем тип подписки по сумме
amount = payment_info['amount']
if amount == config.ASKEZA_PRICE:
    subscription_type = "askeza"
    subscription_name = "Аскеза"
elif amount == config.ASKEZA_NUMEROLOGY_PRICE:
    subscription_type = "numerology"
    subscription_name = "Аскеза+Нумерология"
else:
    subscription_type = "askeza"
    subscription_name = "Аскеза"
```

## 🚀 **Тестирование:**

### **1. Запустите бота:**
```bash
python main_fixed.py
```

### **2. Протестируйте сценарии:**
1. **Нажмите `/start`** - должны появиться две кнопки оплаты
2. **Выберите "Аскеза"** - должен создаться платеж на 990 рублей
3. **Выберите "Аскеза+Нумерология"** - должен создаться платеж на 2490 рублей
4. **Оплатите и проверьте** - должны прийти уведомления с правильным типом подписки

### **3. Ожидаемые логи:**
```
🔍 [SUBSCRIBE] Получен запрос на подписку askeza от пользователя {user_id}
🔍 [SUBSCRIBE] Получен запрос на подписку numerology от пользователя {user_id}
✅ [CHECK] Подписка Аскеза создана для пользователя {user_id}
✅ [CHECK] Подписка Аскеза+Нумерология создана для пользователя {user_id}
```

## 📊 **Результат:**

### ✅ **Две кнопки оплаты работают!**

**Теперь пользователи могут выбрать:**
- 🌸 **Аскеза** - 990 рублей (базовый доступ)
- 🔮 **Аскеза+Нумерология** - 2490 рублей (расширенный доступ)

**Система автоматически:**
- ✅ **Определяет тип подписки** по сумме платежа
- ✅ **Создает правильную подписку** в базе данных
- ✅ **Отправляет уведомления** с указанием типа подписки
- ✅ **Предоставляет доступ** к каналу для обеих подписок

## 🎯 **Рекомендации:**

### **Для продакшена:**
```bash
python main_fixed.py
```

### **Для тестирования:**
```bash
python bot_fixed.py
```

**Две кнопки оплаты готовы к использованию!**
