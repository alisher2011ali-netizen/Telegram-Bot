from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from states import TrainingStates

from database import Database
from keyboards import get_main_kb

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
        "Привет!Выбери упражнение или напиши 'Упражнение Число'",
        reply_markup=get_main_kb(),
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


@router.message(F.text.in_(["Отжимания", "Приседания", "Подтягивания"]))
async def start_fsm(message: Message, state: FSMContext):
    await state.update_data(chosen_exercise=message.text)

    await state.set_state(TrainingStates.waiting_for_count)
    await message.answer(
        f"Выбрано: {message.text}. Сколько раз сделал? (Введи только число)"
    )


@router.message(TrainingStates.waiting_for_count)
async def process_count(message: Message, state: FSMContext, db: Database):
    if not message.text or not message.from_user:
        return
    if not message.text.isdigit():
        await message.answer("Пожалйуста, введи именно число!")
        return

    user_data = await state.get_data()
    exercise = user_data["chosen_exercise"]
    count = int(message.text)

    await db.add_exercise(message.from_user.id, exercise, count)
    total = await db.get_total_reps(message.from_user.id, exercise)

    await message.answer(
        f"Записал {count} ({exercise}). \nВсего: <b>{total}</b>", parse_mode="HTML"
    )

    await state.clear()


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
