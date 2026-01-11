from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command

from database import Database
from keyboards import get_exercises_kb

router = Router()


@router.message(CommandStart())
async def start(message: Message, db: Database):
    """
    Реагирует на команду /start и регистрирует пользователя в базе данных
    """
    if not message.from_user:
        return

    await db.register_user(
        message.from_user.id, message.from_user.username, message.from_user.first_name
    )

    await message.answer(
        "Привет! Выбери упражнение на кнопках ниже и допиши количество через пробел.",
        reply_markup=get_exercises_kb(),
    )


@router.message(F.text.lower() == "статистика")
async def show_stats(message: Message, db: Database):
    print("Хендлер статистики сработал!")
    if not message.from_user:
        return
    stats = await db.get_all_stats(message.from_user.id)
    if not stats:
        await message.answer("У тебя пока нет записей!")
        return

    text = "<b> Твои достижения:</b>\n\n"
    for name, total in stats:
        text += f"🔹 {name}: <b>{total}</b>\n"

    await message.answer(text, parse_mode="HTML")


@router.message(F.text)
async def add_value(message: Message, db: Database):
    if not message.text or not message.from_user:
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            return

        exercise = parts[0].capitalize()
        count = int(parts[1])

        await db.add_exercise(message.from_user.id, exercise, count)
        total = await db.get_total_reps(message.from_user.id, exercise)

        await message.answer(
            f"Записал: {count} ({exercise}). Молодец!\n"
            f"Твой суммарный результат: <b>{total}</b>",
            parse_mode="HTML",
        )
    except (ValueError, IndexError):
        pass
