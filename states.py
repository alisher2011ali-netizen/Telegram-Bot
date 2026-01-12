from aiogram.fsm.state import StatesGroup, State


class TrainingStates(StatesGroup):
    waiting_for_count = State()
