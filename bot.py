import telebot
from telebot import types
import requests
import json
import os
from dotenv import load_dotenv
import logging

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
API_KEY = os.getenv('API_EXCHANGE_KEY')
API_URL = f'https://v6.exchangerate-api.com/v6/{API_KEY}/latest/USD'

if TOKEN is None:
    raise ValueError("Токен TELEGRAM_BOT_TOKEN не найден в файле .env")
    
user_amounts = {}

bot = telebot.TeleBot(token=TOKEN)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@bot.message_handler(commands=['start'])
def start(message):
    user_amounts[message.chat.id] = None
    bot.send_message(message.chat.id, 'Введите сумму, которую хотите перевести в доллары (USD): ')
    bot.register_next_step_handler(message, summa)

def summa(message):
    chat_id = message.chat.id
    try:
        user_amount = int(message.text.strip())
        if user_amount <= 0:
            raise ValueError("Число должно быть больше 0")
        
        user_amounts[chat_id] = user_amount
        
    except ValueError as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}. Попробуйте еще раз ввести сумму:")
        bot.register_next_step_handler(message, summa)
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton('RUB', callback_data='RUB')
    btn2 = types.InlineKeyboardButton('KZT', callback_data='KZT')
    btn3 = types.InlineKeyboardButton('EUR', callback_data='EUR')
    btn4 = types.InlineKeyboardButton('Другое значение', callback_data='else')
    markup.add(btn1, btn2, btn3, btn4)
    
    bot.send_message(message.chat.id, "Выберите валюту", reply_markup=markup)
        
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    chat_id = call.message.chat.id

    # Подтверждение обработки callback_query
    bot.answer_callback_query(call.id)

    logging.info(f"Обработка callback: {call.data} для чата {chat_id}")

    amount = user_amounts.get(chat_id)

    if amount is None:
        bot.send_message(chat_id, "Кажется, я забыл вашу сумму. Пожалуйста, начните заново: /start")
        return

    currency_code = call.data

    if currency_code == 'else':
        bot.send_message(chat_id, "Введите 3-буквенный код валюты (например, JPY, GBP):")
        bot.register_next_step_handler(call.message, handle_custom_currency)
        return
    try:
        res = requests.get(url=API_URL, timeout=10)  # Установлен таймаут 10 секунд
        res.raise_for_status()
        data = res.json()
        rate = data['conversion_rates'].get(currency_code)

        if rate is None:
            bot.send_message(chat_id, f"Не удалось найти курс для валюты {currency_code}.")
            return

        result = amount * rate

        bot.send_message(call.message.chat.id, f'Результат: <b>{amount} USD = {result:.2f} {currency_code}</b>', parse_mode='HTML')

    except requests.exceptions.Timeout:
        logging.error("Превышено время ожидания ответа от API")
        bot.send_message(chat_id, "Превышено время ожидания ответа от API. Попробуйте позже.")
    except json.JSONDecodeError:
        logging.error("Ошибка при обработке JSON-ответа от API")
        bot.send_message(chat_id, "Произошла ошибка при обработке ответа от API.")

def handle_custom_currency(message):
    chat_id = message.chat.id
    custom_code = message.text.strip().upper()
    
    class CallMock:
        def __init__(self, data, message):
            self.data = data
            self.message = message
            self.chat_id = message.chat.id
    mock_call = CallMock(data=custom_code, message=message)
    callback(mock_call)


bot.polling(none_stop=True)
