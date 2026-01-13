from aiogram.fsm.state import StatesGroup, State


class TrainingStates(StatesGroup):
    waiting_for_count = State()
    waiting_for_delete_confirm = State()
