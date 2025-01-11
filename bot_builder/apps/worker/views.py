from django.shortcuts import render
from apps.worker.models import Events
from apps.bot.models import BotUser, Bot_Message
from django.http import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse, HttpResponseBadRequest
from apps.bot.bot_core import tg_bot as bot_token_main

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import time 

import threading




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import urllib.parse


def send_delayed_telegram_message(user_id):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    share_url = f"https://t.me/share/url?url=&text={urllib.parse.quote('Привет! Давай помечтаем вместе с @BCS_NewYear_bot')}"
    
    data_second = {
        "chat_id": user_id,
        "text": "Чтобы помечтать ещё раз, нажмите ниже",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Помечтать", "callback_data": "start_opros"},
                    {"text": "Поделиться ботом", "url": share_url},
                ]
            ]
        }
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа
    return response.json()  # Возвращение ответа Telegram













import random
import time
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

class TelegramSender:
    def __init__(self, bot_tokens):
        self.bot_tokens = bot_tokens
        self.last_request_time = {}
        self.min_delay = 3  # Минимальная задержка между запросами

    def send_message(self, user_id, caption, path_on_the_photo, photo):
        # Выбираем токен с наименьшим временем последнего запроса
        bot_token = min(self.bot_tokens, key=lambda token: self.last_request_time.get(token, 0))
        
        # Проверяем и ожидаем между запросами
        current_time = time.time()
        last_request = self.last_request_time.get(bot_token, 0)
        if current_time - last_request < self.min_delay:
            time.sleep(self.min_delay - (current_time - last_request))
        
        
        
        try:
            url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
            path_photo = str(path_on_the_photo.replace('<code>', '').replace('</code>', '').split(" ")[-1])
            encoded_path = urllib.parse.quote(path_photo)
            # /root/project/balancer-v2.0/face_to_face_server0/media/67/men/photo_вертикальный_12_men_вертикальный.png
            
            print('\npath_photo', path_photo)
            data = {
                "chat_id": user_id,
                "caption": f'{caption}\n\n{path_on_the_photo.split(" ")[-1]}',
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps({
                    "inline_keyboard": [
                        [
                            {"text": "Удалить", "url": f"http://91.218.245.239:8091/deletepath{encoded_path}"},
                        ]
                    ]
                })
            }
            files = {'photo': photo}

            response = requests.post(url, data=data, files=files, timeout=10)

            print("Отправка пользователю")
            
            # Обработка возможных ошибок
            if response.status_code == 429:
                # Если получена ошибка Too Many Requests
                retry_after = int(response.headers.get('Retry-After', 30))
                time.sleep(retry_after)
                return self.send_message(user_id, caption, path_on_the_photo, photo)
            
            response.raise_for_status()
            self.last_request_time[bot_token] = time.time()
            
            return response.json()
        
        except requests.exceptions.RequestException as e:
            print(f"Ошибка отправки: {e}")
            # Можно добавить логирование
            return None


bot_tokens = [
    '7713483058:AAEc50C1kv_OEsT0oimmGi3SCZE7SUrxheE',
    '6949967515:AAGeDlYbz6AFI8VL4_FwrYO5TDSrEVotZ-s',
    '7723194099:AAHQK5NnxPxnkVl3Vu4sxtTgnqh1RKtuIIY',
    '7784835629:AAHqxQ6dYExuWHgKiwO0fGe68idmbKC4k14',
    '6332991609:AAGtXLnq48-B7QULQRuuVhuZjK6hjGYtL3s',
    '7250124821:AAHeJumXdqta6iVevsucxSZ_2MyYLsc6wV4',
    '6878965634:AAHhtT_BrhcOlP-2-oC874ErgDH3n3zGtkg',
    '7189775199:AAFVckwBLNMu1qVBWwPThKHEVlpdnkSYlMs',
    '7848719772:AAErFfBS4pLJPU9DQ-wNYXskZJDbWoCJRaI',
    '8052596307:AAGP0yVcp7VWK2jed6NCeJlFqFgg2BJQoYM',
    '7891571735:AAFum-xWYx6tue6-N_y75kYYWWGe61AYQTE',
    '7434266925:AAFRzWcKVqRB47VFo6DbrncVr2axG3CrWlQ',
    '7868902209:AAE6pwblzLzJEkpfBD2PAMC5PSqC5Uli19A',
    '7654755892:AAGRXb6fUbflavigVR2FqGsQ1El9EDi93ZU',
]
telegram_sender = TelegramSender(bot_tokens)

@csrf_exempt
def task_complete_alert(request):
    if request.method == "POST":
        try:
            user_id = request.POST.get('chat_id')
            caption = request.POST.get('caption')
            photo = request.FILES.get('photo')
            path_on_the_photo = request.POST.get('path_on_the_photo')
            target_photo_status = request.POST.get('target_photo_status')
            if target_photo_status == 'False':
                if not user_id or not caption or not photo:
                    return JsonResponse({"error": "Не все данные предоставлены"}, status=400)

                result = telegram_sender.send_message(user_id, caption, path_on_the_photo, photo)
                print(f"Отправленно пользователю: {caption}\n{result}\n\n")
                if result:
                    return JsonResponse(result, status=200)
                else:
                    return JsonResponse({"error": "Не удалось отправить сообщение"}, status=500)
                
            
            if target_photo_status == 'True':
                url = f'https://api.telegram.org/bot{bot_token_main}/sendPhoto'
                data = {
                    "chat_id": user_id,
                    "caption": caption,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,

                }
                files = {'photo': photo}
                
                response = requests.post(url, data=data, files=files, timeout=10)
                json_response = response.json()
                send_delayed_telegram_message(user_id)
                return JsonResponse(json_response, status=200)


        except Exception as e:
            return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

    return JsonResponse({"error": "Метод не поддерживается"}, status=405)

















from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import openpyxl
import os

@csrf_exempt
def get_user_logs(request):

    file_path = '/root/project/balancer-v2.0/face_to_face_server0/xlsx/user_log.xlsx'
    
    try:
        # Получаем данные
        logs = BotUser.objects.all()
        
        # Создаем Excel файл
        workbook = openpyxl.Workbook()
        worksheet = workbook.active

        # Заголовки
        headers = [
            'Telegram ID',
            'Имя пользователя',
            'Фамилия пользователя',
            'Username',
            'Язык',
            'Премиум',
            'Состояние',
            'ID последнего сообщения',
            'Путь к фото',
            'Сумма инвестиций',
            'Период',
            'Интерес',
            'Тип инвестора',
            'Гендер',
            'Количество генераций',
            'Сумма инвестиций первый раз',
            'Период первый раз',
            'Интерес первый раз',
            'Тип инвестора первый раз',
            'Гендер первый раз',
            'Формат'
        ]
        worksheet.append(headers)

        # Записываем данные
        for log in logs:
            row = [
                str(log.tg_id) if log.tg_id else '',
                log.first_name if log.first_name else '',
                log.last_name if log.last_name else '',
                log.username if log.username else '',
                log.language if log.language else '',
                'Да' if log.premium else 'Нет',
                log.state if log.state else '',
                str(log.last_message_id) if log.last_message_id else '',
                log.photo.url if log.photo else '',
                log.summa if log.summa else '',
                log.period if log.period else '',
                log.interes if log.interes else '',
                log.type_investor if log.type_investor else '',
                log.gender if log.gender else '',
                log.count_generation if log.count_generation else '',
                log.summa_first if log.summa_first else '',
                log.period_first if log.period_first else '',
                log.interes_first if log.interes_first else '',
                log.type_investor_first if log.type_investor_first else '',
                log.gender_first if log.gender_first else '',
                log.format_photo if log.format_photo else ''
            ]
            worksheet.append(row)

        # Настраиваем ширину колонок
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min((max_length + 2), 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width

        # Создаем директорию если её нет
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Сохраняем файл
        workbook.save(file_path)
        
        # Отправляем файл
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="user_log.xlsx"'
        return response

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Ошибка: {str(e)}")
        print(f"Детали:\n{error_details}")
        return HttpResponse(f'Ошибка сервера: {str(e)}', status=500)

    finally:
        # Удаляем временный файл если он существует
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass




# import random
# import requests
# @csrf_exempt
# def task_complete_alert(request):
#     if request.method == "POST":
#         try:
#             # Получение данных из запроса
#             user_id = request.POST.get('chat_id')
#             caption = request.POST.get('caption')
#             photo = request.FILES.get('photo')

#             if not user_id or not caption or not photo:
#                 return JsonResponse({"error": "Не все данные предоставлены"}, status=400)

#             # Отправка фото




# #Временно - потом раскоментировать 9 строку
#             bot_tokens = [
#                 '7505930029:AAE2pSpnQGjVyN8K-HNhZ8dxepkJzIpzpcY',
#                 '7713483058:AAEc50C1kv_OEsT0oimmGi3SCZE7SUrxheE',
#                 '6949967515:AAGeDlYbz6AFI8VL4_FwrYO5TDSrEVotZ-s',
#                 '7723194099:AAHQK5NnxPxnkVl3Vu4sxtTgnqh1RKtuIIY',
#                 '7784835629:AAHqxQ6dYExuWHgKiwO0fGe68idmbKC4k14',
#                 '6332991609:AAGtXLnq48-B7QULQRuuVhuZjK6hjGYtL3s',
#                 '7250124821:AAHeJumXdqta6iVevsucxSZ_2MyYLsc6wV4',
#                 '6878965634:AAHhtT_BrhcOlP-2-oC874ErgDH3n3zGtkg',
#                 '7189775199:AAFVckwBLNMu1qVBWwPThKHEVlpdnkSYlMs',
#                 '7848719772:AAErFfBS4pLJPU9DQ-wNYXskZJDbWoCJRaI',
#                 '8052596307:AAGP0yVcp7VWK2jed6NCeJlFqFgg2BJQoYM',
#                 '7891571735:AAFum-xWYx6tue6-N_y75kYYWWGe61AYQTE',
#                 '7434266925:AAFRzWcKVqRB47VFo6DbrncVr2axG3CrWlQ',
#                 '7868902209:AAE6pwblzLzJEkpfBD2PAMC5PSqC5Uli19A',
#                 '7654755892:AAGRXb6fUbflavigVR2FqGsQ1El9EDi93ZU',
#             ]
            
#             # Выбираем случайный токен
#             bot_token = random.choice(bot_tokens)




#             time.sleep(30)
#             url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
#             data = {
#                 "chat_id": user_id,
#                 "caption": caption,
#                 "parse_mode": "HTML",
#                 "disable_web_page_preview": True,
#             }
#             files = {'photo': photo}
#             response = requests.post(url, data=data, files=files)
#             response.raise_for_status()  # Проверка статуса ответа

#             telegram_response_first = response.json()

#             # Отправка второго сообщения
#             send_delayed_telegram_message(user_id)

#             return JsonResponse(telegram_response_first, status=200)

#         except requests.exceptions.RequestException as e:
#             # Обработка ошибок при запросах к Telegram API
#             error_text = f"Ошибка генерации!\n\n{e}"
#             send_error_message(error_text)
#             return JsonResponse({"error": f"Ошибка запроса: {str(e)}"}, status=500)

#         except Exception as e:
#             # Обработка других ошибок
#             return JsonResponse({"error": f"Произошла ошибка: {str(e)}"}, status=500)

#     # Если метод не POST
#     return JsonResponse({"error": "Метод не поддерживается"}, status=405)





















def send_error_message(error_text):
    #Временно - потом раскоментировать 9 строку
    bot_tokens = [
        '7713483058:AAEc50C1kv_OEsT0oimmGi3SCZE7SUrxheE',
        '6949967515:AAGeDlYbz6AFI8VL4_FwrYO5TDSrEVotZ-s',
        '7723194099:AAHQK5NnxPxnkVl3Vu4sxtTgnqh1RKtuIIY',
        '7784835629:AAHqxQ6dYExuWHgKiwO0fGe68idmbKC4k14',
        '6332991609:AAGtXLnq48-B7QULQRuuVhuZjK6hjGYtL3s',
        '7250124821:AAHeJumXdqta6iVevsucxSZ_2MyYLsc6wV4',
        '6878965634:AAHhtT_BrhcOlP-2-oC874ErgDH3n3zGtkg',
        '7189775199:AAFVckwBLNMu1qVBWwPThKHEVlpdnkSYlMs',
        '7848719772:AAErFfBS4pLJPU9DQ-wNYXskZJDbWoCJRaI',
        '8052596307:AAGP0yVcp7VWK2jed6NCeJlFqFgg2BJQoYM',
        '7891571735:AAFum-xWYx6tue6-N_y75kYYWWGe61AYQTE',
        '7434266925:AAFRzWcKVqRB47VFo6DbrncVr2axG3CrWlQ',
        '7868902209:AAE6pwblzLzJEkpfBD2PAMC5PSqC5Uli19A',
        '7654755892:AAGRXb6fUbflavigVR2FqGsQ1El9EDi93ZU',
    ]
                
    
    # Выбираем случайный токен
    bot_token = random.choice(bot_tokens)
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    data = {
        "chat_id": -1002271195442,  # ID администратора
        "text": error_text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
        "reply_markup": {
            "inline_keyboard": [
                [
                    {"text": "Прислать фото", "callback_data": "after_error_send_photo"},
                    {"text": "Пройти опрос", "callback_data": "start_opros"}
                ]
            ]
        }
    }
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при отправке сообщения об ошибке: {e}")


# @csrf_exempt
# def task_error_alert(request):
#     if request.method == "POST":
#         try:
#             # Получение данных из запроса
#             user_id = request.POST.get('chat_id')

#             user = BotUser.objects.get(tg_id=int(user_id))

#             # URL для отправки сообщения в Telegram
#             url = f'https://api.telegram.org/bot{bot_token_main}/sendPhoto'

#             text = '''
# Ошибка генерации!\n
# Последний шаг!\n
# Для отправки фото нажмите ниже 👇'''

#             photo_path = '/root/project/bot_bulder/bot_builder/media/primer.jpg'
#             # Открываем файл для отправки
#             with open(photo_path, 'rb') as photo_file:
#                 # files = {'photo': photo_file}
                
#                 data = {
#                     "chat_id": user_id,
#                     "caption": text,
#                     "parse_mode": "HTML",
#                     "disable_web_page_preview": True,
#                     "reply_markup": json.dumps({
#                         "inline_keyboard": [
#                             [
#                                 {
#                                     "text": "Прислать фото",
#                                     "web_app": {
#                                         "url": f"https://bcs-invest-balanser.site/user_photo_upload?tg_id={user_id}"
#                                     }
#                                 },
#                                 {
#                                     "text": "Пройти опрос",
#                                     "callback_data": "start_opros"
#                                 }
#                             ]
#                         ]
#                     })
#                 }

#                 response = requests.post(url, data=data, files=files)
                
#                 if response.status_code == 200:
#                     response_data = response.json()
#                     message_id = response_data['result']['message_id']
#                     user.last_message_id = message_id
#                     user.save()
                    
#                     return JsonResponse(response.json(), status=200)

#         except requests.exceptions.RequestException as e:
#             # Обработка ошибок при запросе к Telegram
#             return JsonResponse({"error": f"error message: {str(e)}"}, status=500)

#         except Exception as e:
#             # Обработка других ошибок
#             return JsonResponse({"error": f"error: {str(e)}"}, status=500)

#     # Если метод не POST
#     return JsonResponse({"error": "Not Post"}, status=405)




@csrf_exempt
def task_error_alert(request):
    if request.method == "POST":
        try:
            user_id = request.POST.get('chat_id')
            user = BotUser.objects.get(tg_id=int(user_id))

            # URL для отправки текстового сообщения в Telegram
            url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'

            text = '''
Ошибка генерации!\n
Для повторной отправки фото нажмите ниже 👇'''

            data = {
                "chat_id": user_id,
                "text": text,  # <-- Используем поле "text", а не "caption"
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
                "reply_markup": json.dumps({
                    "inline_keyboard": [
                        [
                            {
                                "text": "Прислать фото",
                                "web_app": {
                                    "url": f"https://bcs-invest-balanser.site/user_photo_upload?tg_id={user_id}"
                                }
                            },
                            {
                                "text": "Пройти опрос",
                                "callback_data": "start_opros"
                            }
                        ]
                    ]
                })
            }

            # Отправляем POST-запрос на сервер Telegram Bot API
            response = requests.post(url, data=data)

            if response.status_code == 200:
                response_data = response.json()
                message_id = response_data['result']['message_id']
                user.last_message_id = message_id
                user.save()
                return JsonResponse(response_data, status=200)
            else:
                return JsonResponse({"error": response.text}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return JsonResponse({"error": f"error message: {str(e)}"}, status=500)
        except Exception as e:
            return JsonResponse({"error": f"error: {str(e)}"}, status=500)

    return JsonResponse({"error": "Not Post"}, status=405)









def send_status_message(user_id, message):
    url = f'https://api.telegram.org/bot{bot_token_main}/sendMessage'
    
    data_second = {
        "chat_id": user_id,
        "text": f"{message}",
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    
    response = requests.post(url, json=data_second)
    response.raise_for_status()  # Проверка статуса ответа



def delete_message(chat_id, message_id):
    """
    Удаляет сообщение по его message_id.
    """
    url = f"https://api.telegram.org/bot{bot_token_main}/deleteMessage"

    # Параметры запроса
    payload = {
        "chat_id": chat_id,
        "message_id": message_id
    }

    # Выполняем POST-запрос
    response = requests.post(url, json=payload)
    response.raise_for_status()  # Бросит исключение, если статус != 200



from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import PhotoUploadForm

def user_photo_upload(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        tg_id = request.POST.get('tg_id')

        user = BotUser.objects.get(tg_id=int(tg_id))

        if form.is_valid():
            photo = form.cleaned_data['photo']
            user.photo = photo
            user.count_generation += 1
            if user.summa_first == None or user.summa_first == '':
                user.summa_first = user.summa
                user.period_first = user.period
                user.interes_first = user.interes
                user.type_investor_first = user.type_investor
                user.gender_first = user.gender

            user.save()


            with open(user.photo.path, 'rb') as file:
                files = {'user_photo': file}

                data = {
                    'user_id': user.tg_id,
                    'prompt': f'promt_user {user.summa}_{user.period}_{user.interes}_{user.type_investor}_{user.gender}_{user.format_photo}',
                    'format_photo': user.format_photo,
                    'task_end_handler': 'task_end_alert',
                    'generation_or_face_to_face': 'False',
                }
                response = requests.post('http://91.218.245.239:8091/create_task', data=data, files=files)

                if response.status_code == 200:
                    print("Задача успешно создана:", response.json())
                    message = "Успешно! Ожидайте..."

                    if user.last_message_id:
                        # Убираем кнопки у предыдущего сообщения, установив reply_markup=None
                        delete_message(user.tg_id, user.last_message_id)
                        
                    send_status_message(user.tg_id, message)
                else:
                    print(f"Ошибка: {response.status_code}, {response.text}")
                    send_status_message(-1002271195442, message=f"У пользователя {user.tg_id} ошибка при загрузке фото!\n\n{response.status_code}, {response.text}")
                    send_status_message(user.tg_id, message='Возникла ошибка с загрузкой фото! Повторите попытку')


                response_render = render(request, 'photo_input.html', {
                    'form': form,
                    'tg_id': tg_id,
                    'close': True,
                })
                    # Добавляем заголовки безопасности
            
                response_render['X-Content-Type-Options'] = 'nosniff'
                
                return response_render

    else:
        tg_id = request.GET.get('tg_id')
        user = BotUser.objects.get(tg_id=int(tg_id))
        form = PhotoUploadForm()
    
    response_render = render(request, 'photo_input.html', {
        'form': form,
        'tg_id': tg_id,
        'close': False,
    })
    response_render['X-Content-Type-Options'] = 'nosniff'
    
    return response_render