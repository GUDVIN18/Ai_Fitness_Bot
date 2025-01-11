import time
from django.core.management.base import BaseCommand
from apps.bot.models import BotUser
from apps.notification.models import Motivational_Messages
from datetime import datetime, timedelta
from django.utils import timezone
from translate import translate
import re
from open_ai import interact_with_assistant

from datetime import timedelta
from django.utils.timezone import now

from apps.bot.bot_core import tg_bot as bot_token_main
import requests


def send_success_telegram_message(user_id, message):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    data_second = {
        "chat_id": user_id,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram


def clean_response(response):
    if not isinstance(response, str):
        return response
    
    # Удаляем markdown-заголовки (# ...)
    response = re.sub(r'^#+\s*', '', response, flags=re.MULTILINE)
    
    # Удаляем паттерны источников ChatGPT вида: 【4:0†source】
    response = re.sub(r'【\d+:\d+†[^】]*】', '', response)
    
    # Удаляем нежелательные символы †, 【, 】
    special_chars_pattern = r'[†【】]'
    response = re.sub(special_chars_pattern, '', response)
    
    # Больше пробелы не сжимаем и не нормализуем
    
    return response

class Command(BaseCommand):
    def worker_notif():
        try:
            if Motivational_Messages.objects.filter(status=False).exists():
                messages = Motivational_Messages.objects.filter(status=False)
                for message in messages:
                    if message.user.subscription == True:
                        user = message.user
                        send_success_telegram_message(user.tg_id, message.text)
                        message.status = True
                        message.save()
                    else:
                        message.status = True
                        message.save()



            


            # Округляем текущую дату до минут
            yesterday_time_rounded = (now() - timedelta(days=1)).replace(second=0, microsecond=0)
            if Motivational_Messages.objects.filter(created_at=yesterday_time_rounded).exists():
                new_messages = Motivational_Messages.objects.filter(created_at=yesterday_time_rounded)
                for new_message in new_messages:
                    if new_message.user.subscription:  # Проверяем подписку
                        user = new_message.user
                        print('Создаю новое мотивационное сообщение')
                        user_message = f'Сделай мотивационное сообщение (около 40 слов) для {user.first_name}, который тренируется {user.training_frequency} раз в неделю и имеет цель: {user.purpose}.'
                        response = interact_with_assistant(user_message)
                        response_clean = clean_response(response)
                        Motivational_Messages.objects.create(user=user, text=translate(response_clean, user.language_chooce))
                        print('Создано новое мотивационное сообщение после 24 часов')

        except Exception as e:
            print(f"Ошибка при отправке уведа от ai: {e}")
            time.sleep(5)  # Задержка на случай ошибок


    while True:
        worker_notif()
        time.sleep(20)



