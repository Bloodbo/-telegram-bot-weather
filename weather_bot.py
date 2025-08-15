import requests
import time
from datetime import datetime

# Вставь свои токены
TELEGRAM_TOKEN = '7285312566:AAF2xZHj29OC2fH05JopHR0vzIvSKkARjPs'
OPENWEATHERMAP_API_KEY = 'fecd18c530815576fd093eb555fef275'
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/"

# Словарь для смайликов и описания в зависимости от погодных условий
WEATHER_DESCRIPTIONS = {
    'Clear': 'ясно',
    'Clouds': 'облачно',
    'Rain': 'дождь',
    'Drizzle': 'морось',
    'Thunderstorm': 'гроза',
    'Snow': 'снег',
    'Mist': 'туман',
}
WEATHER_EMOJIS = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧️',
    'Drizzle': '🌦️',
    'Thunderstorm': '⛈️',
    'Snow': '❄️',
    'Mist': '🌫️',
}

# Функция для получения текущей погоды с более подробным описанием
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return "Город не найден."

    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    pressure = data['main']['pressure']
    wind_speed = data['wind']['speed']
    description = data['weather'][0]['description']
    weather_main = data['weather'][0]['main']
    emoji = WEATHER_EMOJIS.get(weather_main, '')
    weather_desc = WEATHER_DESCRIPTIONS.get(weather_main, description)

    return (f"Погода в {city}:\n"
            f"Температура: {temp}°C {emoji}\n"
            f"Ощущается как: {feels_like}°C\n"
            f"Влажность: {humidity}%\n"
            f"Давление: {pressure} гПа\n"
            f"Скорость ветра: {wind_speed} м/с\n"
            f"Описание: {weather_desc.capitalize()}")

# Функция для получения прогноза на 5 дней с более детальным описанием
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != "200":
        return "Город не найден."

    forecast = {}
    for entry in data['list']:
        # Дата и время прогноза
        date_time = entry['dt_txt']
        date = date_time.split(' ')[0]
        time_of_day = date_time.split(' ')[1][:5]  # Часы и минуты
        temp = entry['main']['temp']
        description = entry['weather'][0]['description']
        weather_main = entry['weather'][0]['main']
        emoji = WEATHER_EMOJIS.get(weather_main, '')
        weather_desc = WEATHER_DESCRIPTIONS.get(weather_main, description)

        if date not in forecast:
            forecast[date] = []
        forecast[date].append(f"{time_of_day}: {temp}°C {emoji} ({weather_desc})")

    # Формируем вывод на 5 дней с разными периодами дня
    forecast_message = f"Прогноз погоды в {city} на 5 дней:\n"
    for date, weather_list in forecast.items():
        forecast_message += f"\n{datetime.strptime(date, '%Y-%m-%d').strftime('%d %B')}:\n"
        forecast_message += "\n".join(weather_list[:3])  # Утро, день, вечер (3 периода)
    return forecast_message

# Функция для отправки сообщений через Telegram API
def send_message(chat_id, text):
    url = BASE_URL + f"sendMessage?chat_id={chat_id}&text={text}"
    requests.get(url)

# Функция для обработки новых сообщений
def handle_updates(updates):
    for update in updates:
        message = update.get("message")
        if message:
            chat_id = message["chat"]["id"]
            text = message.get("text")

            if text == "/start":
                send_message(chat_id, "Привет! Я бот для показа погоды. Напиши название города, чтобы узнать прогноз на 5 дней.")
            elif text.startswith("/weather"):
                city = text.split("/weather ", 1)[1] if " " in text else ""
                if city:
                    weather_info = get_weather(city)
                    send_message(chat_id, weather_info)
                else:
                    send_message(chat_id, "Пожалуйста, укажи название города после команды /weather.")
            elif text:  # Если текст не является командой, считаем его названием города
                forecast_info = get_forecast(text)
                send_message(chat_id, forecast_info)
            else:
                send_message(chat_id, "Неизвестная команда. Напиши название города, чтобы узнать прогноз на 5 дней.")


# Функция для получения новых сообщений с сервера Telegram
def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    if offset:
        url += f"?offset={offset}"
    response = requests.get(url)
    return response.json()["result"]

# Основной цикл программы для постоянной проверки новых сообщений
def main():
    offset = None
    while True:
        updates = get_updates(offset)
        if updates:
            offset = updates[-1]["update_id"] + 1
            handle_updates(updates)
        time.sleep(1)

if __name__ == "__main__":
    main()
