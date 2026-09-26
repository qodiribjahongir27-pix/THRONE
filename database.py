import aiosqlite

DB_NAME = "throne.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                language TEXT DEFAULT 'uz',
                gold INTEGER DEFAULT 0,
                coin INTEGER DEFAULT 0,
                diamond INTEGER DEFAULT 0,
                elite INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0
            )
        """)

        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row

        cursor = await db.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        return await cursor.fetchone()


async def create_user(
    user_id: int,
    username: str,
    full_name: str,
    gold: int = 0,
    coin: int = 0,
    diamond: int = 0,
    elite: int = 0
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            INSERT OR IGNORE INTO users
            (user_id, username, full_name, gold, coin, diamond, elite)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            username,
            full_name,
            gold,
            coin,
            diamond,
            elite
        ))

        await db.commit()


async def update_user_info(
    user_id: int,
    username: str,
    full_name: str
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET username = ?, full_name = ?
            WHERE user_id = ?
        """, (
            username,
            full_name,
            user_id
        ))

        await db.commit()


async def set_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
            UPDATE users
            SET language = ?
            WHERE user_id = ?
        """, (language, user_id))

        await db.commit()
