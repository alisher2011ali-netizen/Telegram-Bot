from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from states import TrainingStates

from database import Database
from keyboards import get_main_kb, get_undo_kb

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
    """Выводит суммарную статистику по всем упражнениям пользователя."""
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
    """Начинает сценарий записи упражнения через кнопку, запрашивая количество."""
    await state.update_data(chosen_exercise=message.text)

    await state.set_state(TrainingStates.waiting_for_count)
    await message.answer(
        f"Выбрано: {message.text}. Сколько раз сделал? (Введи только число)"
    )


@router.message(TrainingStates.waiting_for_count)
async def process_count(message: Message, state: FSMContext, db: Database):
    """Принимает число повторений и сохраняет их в базу данных."""
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
        f"Записал {count} ({exercise}). \nВсего: <b>{total}</b>",
        parse_mode="HTML",
        reply_markup=get_undo_kb(),
    )

    await state.clear()


@router.message(Command("delete"))
async def delete_all_reps(message: Message, state: FSMContext):
    """Инициирует процесс полной очистки данных пользователя с подтверждением."""
    await state.set_state(TrainingStates.waiting_for_delete_confirm)
    await message.answer(
        "❗ Внимание! Вы собираетесь удалить ВСЮ историю тренировок.\n"
        "После подтверждения это действие уже невозможно отменить.\n\n"
        "Для подтверждения напишите слово <b>УДАЛИТЬ</b> (капсом) или для отмены нажмите /cancel",
        parse_mode="HTML",
    )


@router.message(TrainingStates.waiting_for_delete_confirm)
async def process_delete_confirm(message: Message, state: FSMContext, db: Database):
    if not message.from_user:
        return
    if message.text == "УДАЛИТЬ":
        await db.clear_all_user_data(message.from_user.id)
        await message.answer("💥 Все ваши данные были безвозвратно удалены.")
    else:
        await message.answer("🛡️ Удаление отменено. Данные в безопасности.")

    await state.clear()


@router.message(F.text.lower() == "топ-5")
async def show_top(message: Message, db: Database):
    top_list = await db.get_top_users()

    if not top_list:
        await message.answer("Список лидеров пока пуст!")
        return

    text = "<b>🏆 Топ-5 атлетов:</b>\n\n"
    medals = ["🥇", "🥈", "🥉", "👤", "👤"]

    for i, (name, total) in enumerate(top_list):
        medal = medals[i] if i < len(medals) else "👤"
        text += f"{medal} {name} - <b>{total}</b> повт.\n"

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
        if count > 300:
            message.answer(
                "Ничего себе! Но давай будем честными, введи реальное число."
            )
            return

        await db.add_exercise(message.from_user.id, exercise, count)
        total = await db.get_total_reps(message.from_user.id, exercise)

        await message.answer(
            f"Записал: {count} ({exercise}). Молодец!\n"
            f"Твой суммарный результат: <b>{total}</b>",
            parse_mode="HTML",
            reply_markup=get_undo_kb(),
        )
    except (ValueError, IndexError):
        pass


@router.callback_query(F.data == "undo_last")
async def delete_rep(callback: CallbackQuery, db: Database):
    """Обрабатывает нажатие inline-кнопки для отмены последней записи."""
    if isinstance(callback.message, Message):
        await db.delete_newer_rep(callback.from_user.id)

        await callback.answer("Удалено")
        await callback.message.edit_text("✅ Последняя запись успешно удалена.")
    else:
        await callback.answer("Ошибка: сообщение устарело", show_alert=True)
