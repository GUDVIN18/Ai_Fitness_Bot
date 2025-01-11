from django.core.management.base import BaseCommand
from telebot import TeleBot
from apps.bot.models import BotUser
from apps.worker.models import Events
from apps.bot.bot_core import tg_bot as bot
import json
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Запуск бота кнопки и текст в файле bot_command'


    def save_event(self, user_id, json_data):
        try:
            user, created = BotUser.objects.get_or_create(
                tg_id=user_id,
                defaults={
                    'username': json_data.get('message', {}).get('from', {}).get('username'),
                    'first_name': json_data.get('message', {}).get('from', {}).get('first_name'),
                    'language': json_data.get('message', {}).get('from', {}).get('language'),
                    'premium': json_data.get('message', {}).get('from', {}).get('premium'),
                    'state': json_data.get('message', {}).get('state'),
                }
            )

            a = json_data.get('message', {}).get('text')
            print('text', a)

            event = Events.objects.create(
                user=user,
                status='ACCEPTED',
                update_data=json_data
            )
            if event:
                logger.info(f'Создано событие для пользователя {user_id}')
        except Exception as e:
            logger.error(f'Ошибка при создании события: {str(e)}')



    def handle(self, *args, **options):
        @bot.message_handler(commands=['start'])
        def start_bot(message):
            user_id = message.chat.id
            logger.info(f'Получен текст от пользователя {user_id}')
            
            json_data = {
                "message": {
                    "message_id": message.message_id,
                    "from": {
                        "id": user_id,
                        "is_bot": False,
                        "first_name": message.from_user.first_name,
                        "username": message.from_user.username,
                        "language": message.from_user.language_code,
                        "premium": message.from_user.is_premium
                    },
                    "chat": {
                        "id": user_id,
                        "type": message.chat.type
                    },
                    "date": message.date,
                    "text": message.text,
                    "state": 'command_processing'
                }
            }
            
            self.save_event(user_id, json_data)

            logger.info(f'Получено текстовое сообщение от пользователя {user_id} с JSON {json_data}')
        
            bot.reply_to(message, "Success!")





        @bot.message_handler(func=lambda message: True)
        def handle_message(message):
            user_id = message.chat.id
            
            json_data = {
                "message": {
                    "message_id": message.message_id,
                    "from": {
                        "id": user_id,
                        "is_bot": False,
                        "first_name": message.from_user.first_name,
                        "username": message.from_user.username
                    },
                    "chat": {
                        "id": user_id,
                        "type": message.chat.type
                    },
                    "date": message.date,
                    "text": message.text
                }
            }

            logger.info(f'Получено текстовое сообщение от пользователя {user_id} с JSON {json_data}')
            self.save_event(user_id, json_data)
        





        # Обработка фото
        @bot.callback_query_handler(func=lambda call: True)
        def handle_callback(call):
            user_id = call.from_user.id
            
            json_data = {
                "callback_query": {
                    "id": call.id,
                    "from": {
                        "id": user_id,
                        "is_bot": False,
                        "first_name": call.from_user.first_name,
                        "username": call.from_user.username
                    },
                    "message": {
                        "message_id": call.message.message_id,
                        "chat": {
                            "id": call.message.chat.id,
                            "type": call.message.chat.type
                        }
                    },
                    "data": call.data
                }
            }

            logger.info(f'Получено callback сообщение от пользователя {user_id} с JSON {json_data}')
            
            self.save_event(user_id, json_data)
            
            # Здесь добавьте логику обработки callback query


        self.stdout.write(self.style.SUCCESS('Starting the bot...'))
        
        while True:
            try:
                bot.polling(none_stop=True, timeout=60)
            except Exception as e:
                logger.error(f'Ошибка в polling: {str(e)}')
                continue