import time
from django.core.management.base import BaseCommand
from yookassa import Configuration, Payment
from apps.bot.models import Payment as PaymentBOT
from apps.bot.models import BotUser, UserTraining
from translate import translate
from django.utils import timezone
from datetime import timedelta

from datetime import datetime, timedelta

from apps.bot.bot_core import tg_bot as bot_token_main
import requests


def send_success_notification_telegram_message(user_id, text):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = text
    else:
        text_message = translate(text, user.language_chooce)
    data_second = {
        "chat_id": user_id,
        "text": text_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
       
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram



def send_success_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = "✅ Платеж прошел успешно!"
    else:
        text_message = translate("✅ Платеж прошел успешно!", user.language_chooce)
    data_second = {
        "chat_id": user_id,
        "text": text_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
       
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


def send_error_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'

    user = BotUser.objects.get(tg_id=user_id)
    if user.language_chooce == 'ru':
        text_message = "❌ Платеж не прошел!"
    else:
        text_message = translate("❌ Платеж не прошел!", user.language_chooce)
    
    data_second = {
        "chat_id": user_id,
        "text": text_message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,

    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


class Command(BaseCommand):
    # Настройки Юкасса
    Configuration.account_id = '1006575'  # Ваш идентификатор магазина
    Configuration.secret_key = 'test_377a2T-VX7f7DmnQvNpuoVrxghntsUsJ_3kGJfHg6bo'  # Ваш секретный ключ
    def worker():
        try:
            if PaymentBOT.objects.filter(status='pending').exists():
                payments = PaymentBOT.objects.filter(status='pending')
                for payment in payments:
                    payment_id = payment.payment_id
                    status = payment.status

                    # Получаем информацию о платеже по его ID
                    payment_info = Payment.find_one(payment_id)
                    
                    # Получаем статус платежа
                    payment_info_dict = payment_info.__dict__
                    status = payment_info_dict.get('_PaymentResponse__status')

                    print(f"Статус платежа: {status}")
                    
                    if status == 'succeeded':  # Платеж успешен
                        print(f"Платеж №{payment.id} успешно завершен!")
                        payment.status = 'succeeded'
                        payment.save()
                        user = BotUser.objects.get(tg_id=payment.user_id)
                        user.subscription = True
                        user.subscribe_data_start = datetime.now().date()
                        user.subscribe_data_end = datetime.now().date() + timedelta(days=30)
                        user.save()
                        
                        send_success_telegram_message(payment.user_id)


                        
                    elif status == 'canceled':  # Платеж отменен
                        print(f"Платеж №{payment.id} был отменен.")
                        payment.status = 'canceled'
                        payment.save()
                        send_error_telegram_message(payment.user_id)


                    elif status == 'pending':
                        print(f'Платеж №{payment.id}: Ождание оплаты')

                    time.sleep(1)

        except Exception as e:
            print(f"Ошибка при проверке статуса платежа: {e}")
            time.sleep(5)  # Задержка на случай ошибок

        

        try:
            target_time = timezone.now().replace(second=0, microsecond=0) + timedelta(hours=3)

            if UserTraining.objects.filter(status=False, training_data=target_time).exists():
                trainings = UserTraining.objects.filter(status=False, training_data=target_time)
                for traning in trainings:
                    user_id = traning.user.tg_id
                    traning.status = True
                    traning.save()

                    text = f'Напоминание о тренировке: У тебя тренировка ({traning.name_traning}) через 3 часа!'
                    send_success_notification_telegram_message(user_id, text)


        except Exception as e:
            print(f"Ошибка при напоминании: {e}")
            time.sleep(5)  # Задержка на случай ошибок


    while True:
        worker()
        time.sleep(1)



