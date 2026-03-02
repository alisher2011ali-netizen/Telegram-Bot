from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from bot.utils.gigachat_client import get_ai_response
from bot.database import Database

load_dotenv()

app = FastAPI()
db = Database()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/ask")
async def ask_ai(data: dict):
    user_text = data.get("text", "")

    if not user_text:
        return {"status": "error", "answer": f"Сообщение пустое..."}

    history = [{"role": "user", "content": user_text}]

    ai_answer = await get_ai_response(history)

    model_name = ai_answer[0].model
    tokens_used = ai_answer[0].usage.total_tokens

    await db.add_new_query(
        querier_id=1,
        model_name=model_name,
        query_text=user_text,
        query_len=len(user_text),
        answer_text=ai_answer[1],
        answer_len=len(ai_answer[1]),
        tokens_used=tokens_used,
        response_time=ai_answer[2],
    )

    return {
        "status": "success",
        "answer": ai_answer[1],
    }
