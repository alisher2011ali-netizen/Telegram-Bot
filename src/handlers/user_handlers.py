from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from gigachat.models import Messages, MessagesRole

from utils.gigachat_client import get_ai_response

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer("Привет! Я бот с GigaChat. Напиши мне любой вопрос.")


@router.message(Command("new"))
async def clear_context(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст успешно очищен!")


@router.message(F.text)
async def chat_with_ai(message: Message, state: FSMContext):
    data = await state.get_data()
    history = data.get("history", [])

    history.append(Messages(role=MessagesRole.USER, content=message.text))

    if len(history) > 10:
        history = history[-10:]

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    ai_answer = await get_ai_response(history)
    history.append(Messages(role=MessagesRole.ASSISTANT, content=ai_answer))
    await state.update_data(history=history)

    try:
        await message.answer(ai_answer, parse_mode="Markdown")
    except:
        await message.answer(ai_answer)
