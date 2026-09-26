import aiosqlite

DB_NAME = "throne.db"


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                full_name TEXT DEFAULT '',
                language TEXT DEFAULT 'uz',

                gold INTEGER DEFAULT 0,
                coin INTEGER DEFAULT 0,
                diamond INTEGER DEFAULT 0,

                elite INTEGER DEFAULT 0,
                elite_until TEXT,

                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,

                nickname TEXT DEFAULT '',
                flag TEXT DEFAULT '🏴',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS kingdoms (
                user_id INTEGER PRIMARY KEY,
                name TEXT DEFAULT '',
                flag TEXT DEFAULT '🏰',
                castle_level INTEGER DEFAULT 1,
                kingdom_level INTEGER DEFAULT 1,
                kingdom_gold INTEGER DEFAULT 0,
                population INTEGER DEFAULT 0,
                defense INTEGER DEFAULT 0,
                military_power INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER DEFAULT 1
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS clans (
                clan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                flag TEXT DEFAULT '🏴',
                description TEXT DEFAULT '',
                leader_id INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                treasury INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                clan_role TEXT DEFAULT 'member',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (clan_id, user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                married_at TEXT DEFAULT CURRENT_TIMESTAMP,
                level INTEGER DEFAULT 1,
                family_gold INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,
                games INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,
                duels INTEGER DEFAULT 0,
                duel_wins INTEGER DEFAULT 0,
                tournament_wins INTEGER DEFAULT 0,
                rating INTEGER DEFAULT 0
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,
                notifications INTEGER DEFAULT 1,
                private_messages INTEGER DEFAULT 1,
                sound INTEGER DEFAULT 1
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id INTEGER PRIMARY KEY,
                last_claim TEXT
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                currency TEXT NOT NULL,
                amount INTEGER NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                status TEXT DEFAULT 'lobby',
                phase TEXT DEFAULT 'lobby',
                day_number INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_players (
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role_key TEXT,
                alive INTEGER DEFAULT 1,
                last_words TEXT DEFAULT '',
                PRIMARY KEY (game_id, user_id)
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                target_id INTEGER,
                action TEXT NOT NULL,
                phase TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                tournament_type TEXT NOT NULL,
                status TEXT DEFAULT 'waiting',
                prize_gold INTEGER DEFAULT 0,
                prize_coin INTEGER DEFAULT 0,
                prize_diamond INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        await db.execute("""
            CREATE TABLE IF NOT EXISTS duels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenger_id INTEGER NOT NULL,
                opponent_id INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                winner_id INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
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
            (
                user_id,
                username,
                full_name,
                gold,
                coin,
                diamond,
                elite
            )
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

        await db.execute("""
            INSERT OR IGNORE INTO player_stats (user_id)
            VALUES (?)
        """, (user_id,))

        await db.execute("""
            INSERT OR IGNORE INTO settings (user_id)
            VALUES (?)
        """, (user_id,))

        await db.commit()


async def update_user_info(
    user_id: int,
    username: str,
    full_name: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            UPDATE users
            SET
                username = ?,
                full_name = ?,
                last_seen = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (
            username,
            full_name,
            user_id
        ))

        await db.commit()


async def set_language(
    user_id: int,
    language: str
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
            UPDATE users
            SET language = ?
            WHERE user_id = ?
        """, (
            language,
            user_id
        ))

        await db.commit()


async def update_balance(
    user_id: int,
    currency: str,
    amount: int
):
    allowed = {
        "gold": "gold",
        "coin": "coin",
        "diamond": "diamond"
    }

    column = allowed.get(currency)

    if not column:
        raise ValueError("Noto‘g‘ri valuta")

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            f"""
            UPDATE users
            SET {column} = {column} + ?
            WHERE user_id = ?
            """,
            (amount, user_id)
        )

        await db.commit()


async def get_balance(
    user_id: int,
    currency: str
):
    user = await get_user(user_id)

    if not user:
        return 0

    if currency == "gold":
        return user["gold"]

    if currency == "coin":
        return user["coin"]

    if currency == "diamond":
        return user["diamond"]

    return 0
