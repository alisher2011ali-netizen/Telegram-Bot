from aiogram import Bot, Dispatcher, types, F, html
from aiogram.types import Message, ContentType, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if TOKEN is None:
    raise ValueError("Токен TELEGRAM_BOT_TOKEN не найден в переменных окружения.")

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Открыть веб страницу', web_app=WebAppInfo(url='https://alisher2011ali-netizen.github.io/My_first_project/')))
    
    await message.reply(f'Hello, <b>{message.from_user.full_name}!</b>', parse_mode="HTML", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer('Это справка по боту.')



async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())