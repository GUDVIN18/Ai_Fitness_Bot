import requests

def get_bot_username(token):
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        response = requests.get(url)
        response_data = response.json()
        if response_data['ok']:
            return response_data['result']['username']
        else:
            print(f"Ошибка: {response_data['description']}")
    except Exception as e:
        print(f"Ошибка при запросе: {e}")

# Пример использования
if __name__ == "__main__":
    bot_token = "8083197773:AAGqfVg2eo0cygtyFSCZOSuX33HjoH16xTU"
    username = get_bot_username(bot_token)
    if username:
        print(f"Username бота: {username}")