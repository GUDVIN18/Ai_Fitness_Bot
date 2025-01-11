from django.shortcuts import render
from django.http import HttpResponse
from yookassa import Payment
from apps.bot.models import BotUser 
from apps.bot.bot_core import tg_bot as bot_token_main
import requests


def send_success_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    data_second = {
        "chat_id": user_id,
        "text": "✅ Платеж прошел успешно!",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "В главное меню", "callback_data": "start"},
                ]
            ]
        }
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


def send_error_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    data_second = {
        "chat_id": user_id,
        "text": "❌ Платеж не прошел!",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "В главное меню", "callback_data": "start"},
                ]
            ]
        }
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


def handle_payment_return(request):
    payment_id = request.GET.get('paymentId')  # Получаем идентификатор платежа
    status = request.GET.get('status')  # Получаем статус платежа

    if status == 'success':
        try:
            # Получаем платеж по ID
            payment = Payment.find(payment_id)

            if payment.status == 'succeeded':
                # Находим пользователя по tg_id, который был передан в описание платежа
                user = BotUser.objects.get(tg_id=payment.description)  # Здесь предполагается, что description = tg_id пользователя
                user.subscription = True  # Обновляем статус подписки
                user.save()

                send_success_telegram_message(user.tg_id)
                
                return HttpResponse("Оплата прошла успешно! Ваша подписка активирована.")
            else:
                send_error_telegram_message(user.tg_id)
                return HttpResponse("Оплата не была завершена.")
        except Exception as e:
            return HttpResponse(f"Произошла ошибка при обработке платежа: {e}")
    else:
        return HttpResponse(f"Платеж не был успешен. {status}")
