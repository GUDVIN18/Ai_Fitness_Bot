import uuid
import asyncio
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT

# Настройки Юкасса
Configuration.account_id = '1006575'  # Ваш идентификатор магазина
Configuration.secret_key = 'test_377a2T-VX7f7DmnQvNpuoVrxghntsUsJ_3kGJfHg6bo'  # Ваш секретный ключ

# Функция проверки статуса платежа
async def check_payment_status(payment_id):
    while True:
        try:
            # Получаем информацию о платеже по его ID
            payment_info = Payment.find_one(payment_id)
            
            # Получаем статус платежа
            payment_info_dict = payment_info.__dict__
            status = payment_info_dict.get('_PaymentResponse__status')

            print(f"Статус платежа: {status}")
            
            if status == 'succeeded':  # Платеж успешен
                print("Платеж успешно завершен!")
                break
            elif status == 'canceled':  # Платеж отменен
                print("Платеж был отменен.")
                break
            elif status == 'pending':
                print('Ождание оплаты')

            await asyncio.sleep(1)  # Задержка 1 секунда перед следующим запросом
        except Exception as e:
            print(f"Ошибка при проверке статуса платежа: {e}")
            await asyncio.sleep(5)  # Задержка на случай ошибок


def create_payment(description):
    try:
        payment = Payment.create({
            "amount": {
                "value": "500.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/MealMentor_AIbot"
            },
            "capture": True,
            "description": f"{description}"
        }, uuid.uuid4())

        # Получаем ID платежа
        payment_info_dict = payment.__dict__
        payment_id = payment_info_dict.get('_PaymentResponse__id')
        status = payment_info_dict.get('_PaymentResponse__status')
        print(f"Создан новый платеж с ID: {payment_id}\nStatus: {status}")


        # check_payment_status(payment_id=payment_id)
        PaymentBOT.objects.create(
            payment_id=payment_id,
            status=status,
            user_id=description
        )

        # Получаем URL для подтверждения платежа
        confirmation_url = payment.confirmation.confirmation_url
        return confirmation_url

    except Exception as e:
        print('Проблема при создании платежа:', e)
        return None