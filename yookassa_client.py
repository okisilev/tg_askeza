import logging
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationEventType, WebhookNotification
import uuid
from config import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY, ASKEZA_PRICE, NUMEROLOGY_PRICE

logger = logging.getLogger(__name__)

class YooKassaClient:
    def __init__(self):
        Configuration.account_id = YOOKASSA_SHOP_ID
        Configuration.secret_key = YOOKASSA_SECRET_KEY
    
    def create_payment(self, amount: float, description: str, return_url: str = None) -> dict:
        """Создание платежа в ЮKassa"""
        try:
            payment = Payment.create({
                "amount": {
                    "value": f"{amount:.2f}",
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url or "https://t.me/your_bot"
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "payment_id": str(uuid.uuid4())
                }
            })
            
            return {
                "success": True,
                "payment_id": payment.id,
                "confirmation_url": payment.confirmation.confirmation_url,
                "status": payment.status
            }
        except Exception as e:
            logger.error(f"Ошибка при создании платежа: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_status(self, payment_id: str) -> dict:
        """Получение статуса платежа"""
        try:
            payment = Payment.find_one(payment_id)
            return {
                "success": True,
                "status": payment.status,
                "paid": payment.status == "succeeded"
            }
        except Exception as e:
            logger.error(f"Ошибка при получении статуса платежа {payment_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def process_webhook(self, request_data: dict) -> dict:
        """Обработка webhook от ЮKassa"""
        try:
            notification_object = WebhookNotification(request_data)
            
            if notification_object.event == WebhookNotificationEventType.PAYMENT_SUCCEEDED:
                payment = notification_object.object
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "status": payment.status,
                    "amount": float(payment.amount.value),
                    "currency": payment.amount.currency,
                    "metadata": payment.metadata
                }
            elif notification_object.event == WebhookNotificationEventType.PAYMENT_CANCELED:
                payment = notification_object.object
                return {
                    "success": True,
                    "payment_id": payment.id,
                    "status": payment.status,
                    "cancelled": True
                }
            
            return {
                "success": False,
                "error": "Неизвестный тип события"
            }
        except Exception as e:
            logger.error(f"Ошибка при обработке webhook: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_payment_amount(self, payment_type: str) -> float:
        """Получение суммы платежа по типу"""
        if payment_type == "askeza":
            return ASKEZA_PRICE
        elif payment_type == "numerology":
            return NUMEROLOGY_PRICE
        else:
            raise ValueError(f"Неизвестный тип платежа: {payment_type}")
    
    def get_payment_description(self, payment_type: str) -> str:
        """Получение описания платежа по типу"""
        if payment_type == "askeza":
            return "Доступ к Аскезе на 30 дней"
        elif payment_type == "numerology":
            return "Нумерологический разбор"
        else:
            raise ValueError(f"Неизвестный тип платежа: {payment_type}")
