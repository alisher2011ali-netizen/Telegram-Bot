import os
import time
from gigachat import GigaChat
from gigachat.models import Chat, Messages
from dotenv import load_dotenv

load_dotenv

CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
VERIFY_SSL = os.getenv("GIGACHAT_VERIFY_SSL", "True").lower() == "false"


async def get_ai_response(messages_dict_list: list[dict]):
    """
    Функция отправляет запрос в GigaChat и возвращает ответ.
    """
    try:
        async with GigaChat(
            credentials=CREDENTIALS, verify_ssl_certs=False, scope="GIGACHAT_API_PERS"
        ) as giga:
            formatted_messages = [
                Messages(role=m["role"], content=m["content"])
                for m in messages_dict_list
            ]

            payload = Chat(
                messages=formatted_messages,
                temperature=0.6,
                max_tokens=1000,
            )
            start_time = time.perf_counter()

            response = await giga.achat(payload)

            end_time = time.perf_counter()
            duration = round(end_time - start_time, 2)

            return response, response.choices[0].message.content, duration

    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        if "429" in str(e):
            return "⚠️ Слишком много запросов! Подождите пару секунд, я обрабатываю другой ответ."

        return "Извини, мой искусственный интеллект немного устал. Попробуй позже."
