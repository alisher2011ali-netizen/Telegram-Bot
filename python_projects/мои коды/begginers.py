from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

TOKEN = "token"
CRYPTO_NAME_TO_TICKER = {
    "Bitcoin": "BTCRUB",
    "Ethereum": "ETHRUB",
    "Doge": "DOGERUB"
}


bot = TeleBot(token=TOKEN)


@bot.message_handler(commands=["start"])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=3)
    for crypto_name in CRYPTO_NAME_TO_TICKER.keys():
        item_button = KeyboardButton(crypto_name)
        markup.add(item_button)
    bot.send_message(message.chat.id, "Выберите криптовалюту, цену котрой хотите увидеть. Курс расчитывается с binance.com", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in CRYPTO_NAME_TO_TICKER.keys())
def send_price(message):
    crypto_name = message.text
    print(crypto_name)
    ticker = CRYPTO_NAME_TO_TICKER[crypto_name]
    price = get_price_by_ticker(ticker=ticker)
    bot.send_message(message.chat.id, f"Стоимость {crypto_name} в рублях: {price} RUB.")

def get_price_by_ticker(*, ticker: str) -> float:
    endpoint = "https://api.binance.com/api/v3/ticker/price"
    params = {
        'symbol': ticker,
    }
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        price = float(data['price'])
        return price
    else:
        print(f"Error: {response.status_code}")
        return None

bot.infinity_polling()