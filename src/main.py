from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
import asyncio
import os
from dotenv import load_dotenv

from database import Database
from handlers.user_handlers import router as user_router

load_dotenv()

redis = Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
)

storage = RedisStorage(redis)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if TOKEN is None:
    raise ValueError("Токен TELEGRAM_BOT_TOKEN не найден в переменных окружения.")


bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
db = Database()


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/new", description="🗑 Очистить контекст"),
        BotCommand(command="/statistis", description="📊 Посмотреть статистику"),
    ]
    await bot.set_my_commands(main_menu_commands)


async def main():
    await db.connect()
    await db.create_tables()

    await set_main_menu(bot)

    dp.include_router(user_router)

    print("Бот запущен и база готова!")
    await dp.start_polling(bot, db=db)


if __name__ == "__main__":
    asyncio.run(main())
