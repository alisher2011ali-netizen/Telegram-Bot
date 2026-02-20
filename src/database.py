import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")


class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                host=DB_HOST,
                port=int(DB_PORT),
            )
            print("✅ База данных успешно подключена!")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            import sys

            sys.exit(1)

    async def _execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def _fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def _fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def _fetchval(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)

    async def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            queries_qty INT DEFAULT 0,
            queries_len BIGINT DEFAULT 0,
            answers_len BIGINT DEFAULT 0
        );
        
        CREATE TABLE IF NOT EXISTS queries (
            id SERIAL PRIMARY KEY,
            querier_id BIGINT NOT NULL REFERENCES users(user_id),
            model_name VARCHAR(50),
            query_text TEXT,
            answer_text TEXT,
            tokens_used INT,
            response_time FLOAT,
            rating INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        await self._execute(query)

    async def register_user(self, user_id):
        query = (
            "INSERT INTO users (user_id) VALUES ($1) ON CONFLICT (user_id) DO NOTHING"
        )
        await self._execute(query, user_id)

    async def get_statistics(self, user_id):
        query = "SELECT * FROM users WHERE user_id = $1"
        return await self._fetchrow(query, user_id)

    async def get_query_by_id(self, query_id):
        query = "SELECT * FROM queries WHERE id = $1"
        return await self._fetchrow(query, query_id)

    async def get_queries_by_user_id(self, user_id):
        query = "SELECT * FROM queries WHERE querier_id = $1"
        return await self._fetch(query, user_id)

    async def add_new_query(
        self,
        *,
        querier_id: int,
        model_name: str,
        query_text: str,
        query_len: int,
        tokens_used: int,
        response_time: float,
        answer_text: str,
        answer_len: int,
    ):
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                try:
                    await conn.execute(
                        """
                        INSERT INTO queries (
                            querier_id,
                            model_name,
                            query_text,
                            answer_text,
                            tokens_used,
                            response_time
                        )
                        VALUES ($1, $2, $3, $4, $5, $6)
                        """,
                        querier_id,
                        model_name,
                        query_text,
                        answer_text,
                        tokens_used,
                        response_time,
                    )

                    await conn.execute(
                        """
                        UPDATE users SET
                            queries_qty = queries_qty + 1,
                            queries_len = queries_len + $2, 
                            answers_len = answers_len + $3 
                        WHERE user_id = $1
                        """,
                        querier_id,
                        query_len,
                        answer_len,
                    )
                except Exception as e:
                    print(f"Ошибка транзакции: {e}")
                    raise e
