from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from apps.bot.models import Bot_Message, Bot_Button, BotUser, Text_Castom, UserTraining
from apps.worker.models import Events
import requests
from datetime import datetime
import pandas as pd
import time
from threading import Thread
from datetime import timedelta
import openai
from config import API_CHAT_GPT_KEY
from open_ai import interact_with_assistant
from apps.worker.payment import create_payment
import asyncio
import re
from apps.notification.models import Motivational_Messages
from translate import translate



# from deep_translator import GoogleTranslator

# def translate_message(text: str, target_lang: str = 'en') -> str:
#     try:
#         translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
#         return translated
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return text



class Bot_Handler():
    def __init__(self) -> None:
        self.val = {}  # Инициализируем словарь для хранения переменных


    def format_message_text(self, text):
        """Форматирует текст сообщения, подставляя значения из val"""
        try:
            # Проверяем, является ли text строкой
            if not isinstance(text, str):
                return str(text)
            return text.format(val=type('DynamicValue', (), self.val))
        except KeyError as e:
            print(f"Ошибка форматирования: переменная {e} не найдена")
            return text
        except Exception as e:
            print(f"Ошибка форматирования: {e}")
            return text




    def base(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')




    def start(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные
        print(f'''------------- START 
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем переменные для приветствия
        self.val['user_name'] = user.first_name if user.first_name is not None else user.username
        self.val['text'] = 'добро пожаловать'
        self.val['bot_name'] = 'Bot Builder'
        
        if user.language_chooce == None:
            keyboards_language = InlineKeyboardMarkup()
            keyboards_language.row(
                InlineKeyboardButton(text="🇷🇺 Russia", callback_data='select_language ru'),
                InlineKeyboardButton(text="🇺🇸 English", callback_data='select_language en'),
            )
            sent_message = bot.send_message(user.tg_id, 'Выберите язык бота / Select the language of the bot', reply_markup=keyboards_language, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            user.last_message_id = sent_message.message_id
            user.save()
        else:
            try:
                start_message = Bot_Message.objects.get(current_state='start')
                text = self.format_message_text(start_message.text)
            except Bot_Message.DoesNotExist:
                text = "Ошибка при получении состояния def start()"
                print(text)

            buttons = Bot_Button.objects.filter(message_trigger=start_message)
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

            if len(buttons) >= 2:
                keyboard.row(
                    KeyboardButton(text=translate(buttons[0].text, user.language_chooce)),
                    KeyboardButton(text=translate(buttons[1].text, user.language_chooce)),
                )
            if len(buttons) > 2:
                keyboard.add(
                    KeyboardButton(text=translate(buttons[2].text, user.language_chooce))
                )

            try:
                if user.last_message_id:
                    bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
            except Exception as e:
                print(f'Ошибка {e}')

            sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            user.last_message_id = sent_message.message_id
            user.save()


    def select_language(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        language = callback_data.split(' ')[1]
        user.state = state.current_state
        user.language_chooce = language
        user.save()


        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        # sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()






    def profile(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id

        self.val['first_name'] = user.first_name
        self.val['massa'] = user.massa
        self.val['height'] = user.height
        self.val['age'] = user.age
        self.val['purpose'] = user.purpose if user.purpose != 'Перекомпозиция' else 'Рекомпозиция'
        self.val['subscription'] = f"Да, до {user.subscribe_data_end}" if user.subscription and user.subscribe_data_end else "Нет"

        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        # if user.last_message_id:
        #     bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        user.last_message_id = sent_message.message_id
        user.save()





    def add_traner_input(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        send = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        user.last_message_id = send.message_id
        user.save()




    def training_date_inpt(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        traning_name = message['text']
        traning = UserTraining.objects.create(user=user, name_traning=traning_name)


        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {traning.id}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def e_validate_date(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')




    def create_traning(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        def validate_date_format(date_text, user):
            try:
                # Попробуем распарсить дату в ожидаемом формате
                training_date = datetime.strptime(date_text, '%d-%m-%Y %H:%M')
                return training_date
            except ValueError:
                bot.send_message(
                    user.tg_id,translate("❌ Неверный формат даты\nℹ️ Используйте формат <b>ДД-ММ-ГГГГ ЧЧ:ММ</b>", user.language_chooce), parse_mode='HTML')
                user.state = 'e_validate_date'
                user.save()
                return False

        # Пример обработки
        try:
            training_date = validate_date_format(message['text'], user)
            if training_date:  # Если дата валидная
                training = UserTraining.objects.filter(user=user).order_by('-id').first()
                if training:
                    print('training', training)
                    training.training_data = training_date
                    training.save()

                    self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
                    self.val['time'] = training_date
                    self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

                    # Форматируем текст с использованием переменных
                    text = self.format_message_text(state.text)

                    buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')
                    keyboard = InlineKeyboardMarkup()
                    for button in buttons:
                        keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

                    sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

                    # Сохраняем его ID в пользовательскую модель или в state
                    user.last_message_id = sent_message.message_id
                    user.save()

                else:
                    bot.send_message(
                        user.tg_id,
                        translate("Тренировка не найдена", user.language_chooce)
                    )
                        # Добавляем базовые переменные
        except Exception as e:
            bot.send_message(user.tg_id, translate(f"Ошибка: {e}", user.language_chooce))







    def my_traners(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        tranings = UserTraining.objects.filter(user=user)
        tranings_dict = ""  # Если нужна строка
        for num, traning in enumerate(tranings, start=1):
            # Форматируем дату и время в нужный формат
            formatted_date = (traning.training_data + timedelta(hours=3)).strftime('%Y-%m-%d %H:%M')
            tranings_dict += f'{num}. {traning.name_traning} - {formatted_date}\n\n'
            
        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = tranings_dict

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def change_trainer(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        keyboard = InlineKeyboardMarkup()

        tranings = UserTraining.objects.filter(user=user)
        for num, traning in enumerate(tranings, start=1):
            traning_text = f"{num}. {traning.name_traning} - {traning.training_data}"
            keyboard.add(InlineKeyboardButton(text=translate(traning_text, user.language_chooce), callback_data=f"traning_change {traning.id}"))
        # buttons = Bot_Button.objects.filter(message_trigger=state)
        # for button in buttons:
        #     keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        # sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        
        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        user.last_message_id = sent_message.message_id
        user.save()



    def traning_change(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        traning_id = callback_data.split(' ')[1]

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        keyboard = InlineKeyboardMarkup()

        traning_text_1 = f"Название" if user.language_chooce == 'ru' else f"Name"
        traning_text_2 = f"Дата"
        traning_text_3 = f"Удалить"
        keyboard.row(
            InlineKeyboardButton(text="Название" if user.language_chooce == 'ru' else translate(traning_text_1, user.language_chooce), callback_data=f"traning_chng_name {traning_id}"),
            InlineKeyboardButton(text=translate(traning_text_2, user.language_chooce), callback_data=f"traning_chng_date {traning_id}"),
            InlineKeyboardButton(text=translate(traning_text_3, user.language_chooce), callback_data=f"traning_delete {traning_id}"),
        )
        # buttons = Bot_Button.objects.filter(message_trigger=state)
        # for button in buttons:
        #     keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))
        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)


        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        user.last_message_id = sent_message.message_id
        user.save()



    def traning_delete(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        traning_id = callback_data.split(' ')[1]
        obj = UserTraining.objects.get(id=traning_id)
        obj_text = obj.name_traning

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = obj_text  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {traning_id}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
        bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        obj.delete()




    def traning_chng_name(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        traning_id = callback_data.split(' ')[1]
        user.temporary_training_id = traning_id

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = traning_id  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {traning_id}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')



    def traning_save_name(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        traning_id = user.temporary_training_id
        traning = UserTraining.objects.get(id=traning_id)
        traning.name_traning = message['text']
        traning.save()

        user.temporary_training_id = None
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        send = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')
        user.last_message_id = send.message_id
        user.save()







    def traning_chng_date(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        traning_id = callback_data.split(' ')[1]
        user.temporary_training_id = traning_id

        user.state = state.current_state
        user.save()



        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {traning_id}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)
            
        bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')



    def traning_save_date(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        def validate_date_format(date_text, user):
            try:
                training_date = datetime.strptime(date_text, '%d-%m-%Y %H:%M')
                return training_date
            except ValueError:
                bot.send_message(
                    user.tg_id,translate("❌ Неверный формат даты\nℹ️ Используйте формат <b>ДД-ММ-ГГГГ ЧЧ:ММ</b>", user.language_chooce), parse_mode='HTML')
                user.state = 'e_date_save_date'
                user.save()
                return False

        # Пример обработки
        try:
            training_date = validate_date_format(message['text'], user)
            if training_date:  # Если дата валидная
                traning_id = user.temporary_training_id
                training = UserTraining.objects.get(id=traning_id)
                if training:
                    training.training_data = training_date
                    training.save()

                    user.temporary_training_id = None
                    user.save()

                    self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
                    self.val['time'] = training_date
                    self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

                    # Форматируем текст с использованием переменных
                    text = self.format_message_text(state.text)

                    buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')
                    keyboard = InlineKeyboardMarkup()
                    for button in buttons:
                        keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

                    sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

                    # Сохраняем его ID в пользовательскую модель или в state
                    user.last_message_id = sent_message.message_id
                    user.save()

                else:
                    user.temporary_training_id = None
                    user.save()
                    bot.send_message(
                        user.tg_id,
                        translate("Тренировка не найдена", user.language_chooce)
                    )
                        # Добавляем базовые переменные
        except Exception as e:
            user.temporary_training_id = None
            user.save()
            bot.send_message(user.tg_id, translate(f"Ошибка: {e}", user.language_chooce))



    
    def menus(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['subscription'] = user.subscription
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        keyboard = InlineKeyboardMarkup()

        if user.subscription is not True:
            description = f"{user.tg_id}"

            payment_url = create_payment(description)

            text_castom = Text_Castom.objects.get(condition="Подписка не оплачена")
            text = text_castom.text
            keyboard.add(InlineKeyboardButton(text=translate("Оплатить", user.language_chooce), url=payment_url))




        
        elif user.subscription == True and (user.menu == '' or user.menu == ' ' or user.menu == None):
            text_castoms = Text_Castom.objects.get(condition="Без меню")
            text = text_castoms.text
            keyboard.add(InlineKeyboardButton(text=translate("Составить новое меню", user.language_chooce), callback_data=f"next"))

        elif user.subscription == True and (user.menu != '' or user.menu != ' ' or user.menu != None):
            text = user.menu
            keyboard.add(InlineKeyboardButton(text=translate("Составить новое меню", user.language_chooce), callback_data=f"next"))

        buttons = Bot_Button.objects.filter(message_trigger=state)
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='Markdown')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def trainer_ai_input(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)


        if user.subscription is not True:
            description = f"{user.tg_id}"

            payment_url = create_payment(description)
            keyboards = InlineKeyboardMarkup()
            text_castom = Text_Castom.objects.get(condition="Подписка не оплачена")
            text = text_castom.text
            keyboards.add(InlineKeyboardButton(text=translate("Оплатить", user.language_chooce), url=payment_url))
            keyboards.add(InlineKeyboardButton(text=translate("Назад", user.language_chooce), callback_data='start'))
            # if user.last_message_id:
            #     # Убираем кнопки у предыдущего сообщения, установив reply_markup=None
            #     bot.edit_message_reply_markup(chat_id=user.tg_id, 
            #                                 message_id=user.last_message_id, 
            #                                 reply_markup=None)

            sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboards, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            user.last_message_id = sent_message.message_id
            user.save()


        else:
            buttons = Bot_Button.objects.filter(message_trigger=state)
            keyboard = InlineKeyboardMarkup()
            for button in buttons:
                keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))


            # if user.last_message_id:
            #     # Убираем кнопки у предыдущего сообщения, установив reply_markup=None
            #     bot.edit_message_reply_markup(chat_id=user.tg_id, 
            #                                 message_id=user.last_message_id, 
            #                                 reply_markup=None)

            sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            user.last_message_id = sent_message.message_id
            user.save()



    def trainer_ai_send(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.council = message['text']
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)


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

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f"{button.data} {button.text}"))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()


        #Отправка в гбт
        text_custom = Text_Castom.objects.get(condition="Вопрос ИИ-тренеру")
        user_message = f"{text_custom.text}. Впорос пользователя: {user.council}. Меню пользователя: {user.menu}"
        response = interact_with_assistant(user_message)
        response_clean = clean_response(response)

        keyboards = InlineKeyboardMarkup()
        keyboards.add(InlineKeyboardButton(text=translate("В главное меню", user.language_chooce), callback_data='start'))
        sent_message = bot.send_message(user.tg_id, translate(response_clean, user.language_chooce), parse_mode='Markdown', reply_markup=keyboards)

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def next(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=button.data))


        # if user.last_message_id:
        #     # Убираем кнопки у предыдущего сообщения, установив reply_markup=None
        #     bot.edit_message_reply_markup(chat_id=user.tg_id, 
        #                                 message_id=user.last_message_id, 
        #                                 reply_markup=None)
        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()




    #Фиксируем введеное имя
    def user_first_name(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.first_name = message['text']
        user.last_input_message_id = message['message_id']
        user.state = state.current_state
        user.save()

        if user.last_input_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)


        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()

        # Добавляем все кнопки в одну строку
        keyboard.row(
            *[InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}') for button in buttons]
        )
        
        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        # Отправляем сообщение с клавиатурой
        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    
    def user_gender(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}'))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    
    def user_gender_change(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.gender = callback_data.split(' ')[1]
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=button.data))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)


        # if user.last_input_message_id:
        #     bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def user_age_input(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.age = message['text']
        user.last_input_message_id = message['message_id']
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=button.data))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        if user.last_input_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()




    #Фиксируем вес
    def user_massa_input(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.last_input_message_id = message['message_id']
        user.massa = message['text']
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}'))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)


        if user.last_input_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)


        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()

    

    def user_haight_input(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        try:
            self.val = {}  # Очищаем переменные для каждого нового вызова
            print(f'''
                user - {user}
                call_data - {callback_data}
                call_id - {callback_id}
                message - {message}''')

            user.state = state.current_state
            user.last_input_message_id = message['message_id']
            user.height = message['text']
            user.save()

            # Добавляем базовые переменные
            self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
            self.val['user_id'] = user.tg_id
            self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

            # Форматируем текст с использованием переменных
            text = self.format_message_text(state.text)

            buttons = Bot_Button.objects.filter(message_trigger=state)
            keyboard = InlineKeyboardMarkup()

            for button in buttons:
                if user.language_chooce == 'ru':
                    text_iscl=button.text
                else:
                    text_iscl=translate(button.text, user.language_chooce)

                keyboard.add(InlineKeyboardButton(text=text_iscl, callback_data=f'{button.data} {button.text}'))

            if user.last_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

            if user.last_input_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

            sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

            # Сохраняем его ID в пользовательскую модель или в state
            user.last_message_id = sent_message.message_id
            user.save()   
        except Exception as e:
            print('\nОшибка при user_haight_input', e)
            





    def user_purpose(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.purpose = callback_data.split(' ')[1]
        user.products = ' '
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            if button.text == "Продолжить" or button.text == "Continue":
                if user.products is not None and user.products != ' ':
                    if user.language_chooce == 'ru':
                        text_iscl=button.text
                    else:
                        text_iscl=translate(button.text, user.language_chooce)

                    keyboard.add(InlineKeyboardButton(text=text_iscl, callback_data=f'{button.data} {button.text}'))

                else:
                    pass
            else:
                if user.language_chooce == 'ru':
                    text_iscl=f'❌ {button.text}'
                else:
                    text_iscl=f'❌ {translate(button.text, user.language_chooce)}'

                keyboard.add(InlineKeyboardButton(text=text_iscl, callback_data=f'{button.data} {button.text}'))


        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)


            # if user.language_chooce == 'ru':
            #     text_iscl_mes=button.text
            # else:
            #     text_iscl_mes=translate(button.text, user.language_chooce)


        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()




    def choice_product(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем любые временные переменные

        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}
        ''')

        button_text = callback_data.split(' ')[1]

        # Превращаем user.products в список (если поле пустое, будет пустой список)
        selected_products = user.products.split() if user.products else []

        # Тогглим продукт (добавляем, если нет; убираем, если есть)
        if button_text in selected_products:
            selected_products.remove(button_text)
        else:
            selected_products.append(button_text)

        # Записываем обратно в модель (строка через пробел)
        user.products = ' '.join(selected_products)
        user.save()

        # Получаем объект сообщения из БД по current_state
        state_custom = Bot_Message.objects.get(current_state=user.state)

        try:
            # Получаем все кнопки, связанные с этим сообщением
            try:
                buttons = Bot_Button.objects.filter(message_trigger=state_custom).order_by('id')
            except Exception as e:
                print('Ошибка при запросе кнопок:', e)
                return

            updated_buttons = []

            # Проходимся по всем кнопкам и формируем текст + callback_data
            for button in buttons:
                # Считаем, что в базе button.text хранится «чистое» название, например "milk" без значков
                # (Если у вас в базе уже есть "milk✅", лучше каждый раз очищать button.text от "✅❌" перед сравнением)
                clean_text = button.text.strip('✅❌')
                if clean_text == "Продолжить" or clean_text == "Continue":
                    if user.products is not None and user.products != ' ' and user.products != '':
                        new_text = clean_text
                    else:
                        new_text = ""

                elif clean_text in selected_products:
                    new_text = "✅ " + clean_text
                else:
                    new_text = "❌ " + clean_text

                # callback_data формируем так, чтобы при нажатии мы снова получили чистый текст
                new_callback_data = f"{button.data} {clean_text}"


                if user.language_chooce == 'ru':
                    new_text=new_text
                else:
                    new_text=translate(new_text, user.language_chooce)
               
                updated_buttons.append(
                    InlineKeyboardButton(
                        new_text,
                        callback_data=new_callback_data
                    )
                )

            # Создаём объект клавиатуры (каждая кнопка в своём ряду)
            keyboard = InlineKeyboardMarkup([[btn] for btn in updated_buttons])

            # # Обновляем клавиатуру в сообщении
            if user.last_message_id:
                bot.edit_message_reply_markup(
                    chat_id=user.tg_id,  # ID чата
                    message_id=user.last_message_id,  # ID сообщения, в котором нужно обновить клавиатуру
                    reply_markup=keyboard  # Новый объект клавиатуры
                )

        except Exception as e:
            print('Ошибка при нажатии на кнопку:', e)


    def user_product(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        # user.products = callback_data.split(' ')[1]
        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()

        # Добавляем все кнопки в одну строку
        keyboard.row(
            *[InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}') for button in buttons]
        )


        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()





    def user_allergies(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')
        if message['text']:
            user.last_input_message_id = message['message_id']
            user.allergies = message['text'] if message['text'] != "🚫 Есть ли у вас аллергии или непереносимость каких-либо продуктов?" or "🚫 Do you have any allergies or intolerances to any foods?" else "Аллергии ни на что нет"
            user.save()
            if user.last_input_message_id:
                bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)

        user.state = state.current_state
        user.save()

        # if user.allergies == "Аллергии ни на что нет":
        #     if user.last_input_message_id:
        #         # Убираем кнопки у предыдущего сообщения, установив reply_markup=None
        #         bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)
        # else:

        # if user.last_input_message_id:
        #     bot.delete_message(chat_id=user.tg_id, message_id=user.last_input_message_id)


        

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}'))


        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()




    def user_allergies_yes(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        user.state = state.current_state
        user.save()

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = 'Базовое сообщение'  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}'))

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()




    def user_protein(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        otvet = callback_data.split(' ')[1]
        if otvet == 'Да':
            if user.purpose == "Похудение":
                user.protein = "Изолят сывороточного протеина"

            elif user.purpose == "Сушка":
                user.protein = "Гидролизованный сывороточный протеин"

            elif user.purpose == "Массанабор":
                user.protein = "Концетрат сывороточного протеина"

        elif otvet == 'Нет':
            user.protein = "Не использовать протеин в меню"


        user.state = state.current_state
        user.save()
        

        # Добавляем базовые переменные
        
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = f"{otvet}\n{user.purpose}\n{user.protein}"   # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state).order_by('id')
        keyboard = InlineKeyboardMarkup()

        # Подготовим список кнопок
        button_list = [
            InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=f'{button.data} {button.text}')
            for button in buttons
        ]

        # Первая строка с 3 кнопками
        if len(button_list) >= 3:
            keyboard.row(*button_list[:3])

        # Вторая строка с 2 кнопками
        if len(button_list) >= 5:
            keyboard.row(*button_list[3:5])

        # Если кнопок меньше 5, добавим оставшиеся кнопки в отдельные строки
        for button in button_list[5:]:
            keyboard.add(button)

        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()



    def user_traning_day(self, bot, state, user, callback_data, callback_id, message, event):
        if callback_id:
            bot.answer_callback_query(callback_query_id=callback_id)
        self.val = {}  # Очищаем переменные для каждого нового вызова
        print(f'''
            user - {user}
            call_data - {callback_data}
            call_id - {callback_id}
            message - {message}''')

        traninf_day_on_the_week = callback_data.split(' ')[1]
        user.training_frequency = int(traninf_day_on_the_week.replace('+', ' '))

        user.state = state.current_state
        user.save()

        #Собраем все введеные данные и отправляем запрос в GPT
        # user_message = "Дмитрий Мужчина 18 лет 73 кг Массанабор Мясо, овощи Аллергии нет да, Концетрат сывороточного протеина 3 раза в неделю"
        # response = interact_with_assistant(user_message)

        # Добавляем базовые переменные
        self.val['user_name'] = user.name if hasattr(user, 'name') else 'Пользователь'
        self.val['user_id'] = user.tg_id
        self.val['text'] = ''  # Значение по умолчанию

        # Форматируем текст с использованием переменных
        text = self.format_message_text(state.text)

        buttons = Bot_Button.objects.filter(message_trigger=state)
        keyboard = InlineKeyboardMarkup()
        for button in buttons:
            keyboard.add(InlineKeyboardButton(text=translate(button.text, user.language_chooce), callback_data=button.data))


        if user.last_message_id:
            bot.delete_message(chat_id=user.tg_id, message_id=user.last_message_id)

        sent_message = bot.send_message(user.tg_id, translate(text, user.language_chooce), reply_markup=keyboard, parse_mode='HTML')

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()

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


        text_custom = Text_Castom.objects.get(condition="user_prompt_menu")
        user_message = f"{text_custom.text}. {user.first_name}, {user.gender}, {user.age} лет, {user.massa} кг, рост {user.height} см, цель: {user.purpose}, предпочтения по категориям продуктов питания: {user.products}, наличие аллергии: {user.allergies}, употребление протеина: {user.protein}, количесво теренеровок: {user.training_frequency} раз в неделю"
        response = interact_with_assistant(user_message)
        response_clean = clean_response(response)
        user.menu = response_clean
        
        keyboards = InlineKeyboardMarkup()
        keyboards.add(InlineKeyboardButton(text=translate('Сформировать меню заново', user.language_chooce), callback_data='next'))
        keyboards.add(InlineKeyboardButton(text=translate('В главное меню', user.language_chooce), callback_data='start'))
        sent_message = bot.send_message(user.tg_id, translate(response_clean, user.language_chooce), parse_mode='Markdown', reply_markup=keyboards)

        # Сохраняем его ID в пользовательскую модель или в state
        user.last_message_id = sent_message.message_id
        user.save()

        try:
            obj = Text_Castom.objects.get(condition=user.purpose)
            text = obj.text
            bot.send_message(user.tg_id, translate(text, user.language_chooce), parse_mode='HTML')
        except Exception as e:
            print(f"user_traning_day, {e}")


        obj_kreatin = Text_Castom.objects.get(condition="Рекомендации по спорт-питу")
        text_kreatin = obj_kreatin.text
        bot.send_message(user.tg_id, translate(text_kreatin, user.language_chooce), parse_mode='HTML')


        time.sleep(5)
        user_message_motivational_messages = f'Сделай мотивационное сообщения (около 40 слов) для {user.first_name}, который тренеруется {user.training_frequency} раз в неделю и имеет цель в тренировках: {user.purpose}.'
        response_motivational_messages = interact_with_assistant(user_message_motivational_messages)
        response_motivational_messages_clean = clean_response(response_motivational_messages)
        Motivational_Messages.objects.create(user=user, text=translate(response_motivational_messages_clean, user.language_chooce))
