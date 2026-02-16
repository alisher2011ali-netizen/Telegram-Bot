import os
from gigachat import GigaChat
from gigachat.models import Chat, Messages
from dotenv import load_dotenv

load_dotenv

CREDENTIALS = os.getenv("GIGACHAT_CREDENTIALS")
VERIFY_SSL = os.getenv("GIGACHAT_VERIFY_SSL", "True").lower() == "false"


async def get_ai_response(messages_history: list[Messages]):
    """
    Функция отправляет запрос в GigaChat и возвращает ответ.
    """
    try:
        async with GigaChat(
            credentials=CREDENTIALS, verify_ssl_certs=False, scope="GIGACHAT_API_PERS"
        ) as giga:
            payload = Chat(
                messages=messages_history,
                temperature=0.6,
                max_tokens=1000,
            )
            response = await giga.achat(payload)
            return response.choices[0].message.content

    except Exception as e:
        print(f"Ошибка GigaChat: {e}")
        if "429" in str(e):
            return "⚠️ Слишком много запросов! Подождите пару секунд, я обрабатываю другой ответ."

        return "Извини, мой искусственный интеллект немного устал. Попробуй позже."
