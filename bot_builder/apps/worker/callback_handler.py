from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from apps.worker.commands_handler import Bot_Handler


def callback_handler(bot, callback_data, user_id):
    if callback_data == 'button_1':
        print('Вызов 1 функции')
        try:
            Bot_Handler().button_1(bot, user_id, callback_data)
        except Exception as e:
            print('Ошибка в button_1', e)
        


    elif callback_data == 'button_2':
        print('Вызов 2 функции')

        



