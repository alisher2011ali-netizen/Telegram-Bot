import aiosqlite


class Database:
    def __init__(self, db_path) -> None:
        self.db_path = db_path

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT
                );
                """
            )

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS training (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    exercise_name TEXT,
                    value INTEGER,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                );
                """
            )
            await db.commit()

    async def register_user(self, user_id, username, first_name):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
                (user_id, username, first_name),
            )
            await db.commit()

    async def add_exercise(self, user_id, name, value):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO training (user_id, exercise_name, value) VALUES (?, ?, ?)",
                (user_id, name, value),
            )
            await db.commit()

    async def get_total_reps(self, user_id, exercise_name):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT SUM(value) FROM training WHERE user_id = ? AND exercise_name = ?",
                (user_id, exercise_name),
            ) as cursor:
                row = await cursor.fetchone()
                if row and row[0] is not None:
                    return int(row[0])
                return 0

    async def get_all_stats(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT exercise_name, SUM(value) FROM training WHERE user_id = ? GROUP BY exercise_name",
                (user_id,),
            ) as cursor:
                return await cursor.fetchall()
