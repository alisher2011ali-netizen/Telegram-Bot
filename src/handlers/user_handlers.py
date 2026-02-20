from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from gigachat.models import Messages, MessagesRole

from utils.gigachat_client import get_ai_response
from database import *

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, db: Database):
    await db.register_user(message.from_user.id)

    await message.answer("Привет! Я бот с GigaChat. Напиши мне любой вопрос.")


@router.message(Command("new"))
async def clear_context(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Контекст успешно очищен!")


@router.message(Command("statistics"))
@router.message(F.text == "📊 Статистика")
@router.callback_query(F.data == "statistics")
async def get_statistics(event: Message | CallbackQuery, db: Database):
    stats = await db.get_statistics(event.from_user.id)

    if stats["queries_qty"] == 0:
        queries_av = 0
        answers_av = 0
    else:
        queries_av = round(stats["queries_len"] / stats["queries_qty"])
        answers_av = round(stats["answers_len"] / stats["queries_qty"])

    text = (
        f"📊 <b>Ваша статистика:</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"Кол-во запросов: <b>{stats['queries_qty']}</b> раз\n"
        f"Длина всех запросов: <b>{stats['queries_len']}</b> симв\n"
        f"Длина запросов в среднем: <b>{queries_av}</b> симв\n"
        f"Длина всех ответов: <b>{stats['answers_len']}</b> симв\n"
        f"Длина ответов в среднем: <b>~{answers_av}</b> симв"
    )

    if isinstance(event, Message):
        await event.answer(text)
    else:
        await event.message.answer(text)


@router.message(F.text)
async def chat_with_ai(message: Message, state: FSMContext, db: Database):
    data = await state.get_data()
    history = data.get("history", [])

    history.append({"role": "user", "content": message.text})

    if len(history) > 10:
        history = history[-10:]

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    ai_answer, ai_answer_content, response_time = await get_ai_response(history)
    history.append({"role": "assistant", "content": ai_answer_content})
    await state.update_data(history=history)

    model_name = ai_answer.model
    tokens_used = ai_answer.usage.total_tokens

    await db.add_new_query(
        querier_id=message.from_user.id,
        model_name=model_name,
        query_text=message.text,
        query_len=len(message.text),
        answer_text=ai_answer_content,
        answer_len=len(ai_answer_content),
        tokens_used=tokens_used,
        response_time=response_time,
    )

    try:
        await message.answer(ai_answer_content, parse_mode="Markdown")
    except:
        await message.answer(ai_answer_content)
