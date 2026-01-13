from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


def get_main_kb():
    kb = [
        [KeyboardButton(text="Отжимания "), KeyboardButton(text="Приседания ")],
        [KeyboardButton(text="Подтягивания "), KeyboardButton(text="Статистика")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def get_undo_kb():
    button = InlineKeyboardButton(text="↩️ Отменить запись", callback_data="undo_last")
    return InlineKeyboardMarkup(inline_keyboard=[[button]])
