from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_exercises_kb():
    kb = [
        [KeyboardButton(text="Отжимания "), KeyboardButton(text="Приседания ")],
        [KeyboardButton(text="Подтягивания "), KeyboardButton(text="Статистика")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
