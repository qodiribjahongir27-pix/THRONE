import aiosqlite
from datetime import datetime, timezone
from typing import Optional

DB_PATH = "throne.db"


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row

    await db.execute("PRAGMA foreign_keys = ON")
    await db.execute("PRAGMA journal_mode = WAL")
    await db.execute("PRAGMA busy_timeout = 5000")

    return db


async def init_db():
    db = await get_db()

    try:
        await db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT DEFAULT '',
            full_name TEXT DEFAULT '',
            nickname TEXT DEFAULT '',
            flag TEXT DEFAULT '🏳️',
            gold INTEGER DEFAULT 1000,
            coin INTEGER DEFAULT 0,
            diamond INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            elite INTEGER DEFAULT 0,
            elite_expires_at TEXT,
            is_banned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS settings (
            user_id INTEGER PRIMARY KEY,
            language TEXT DEFAULT 'uz',
            notifications INTEGER DEFAULT 1,
            sound INTEGER DEFAULT 1,
            animations INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS player_stats (
            user_id INTEGER PRIMARY KEY,
            games_played INTEGER DEFAULT 0,
            games_won INTEGER DEFAULT 0,
            games_lost INTEGER DEFAULT 0,
            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            duels_played INTEGER DEFAULT 0,
            duels_won INTEGER DEFAULT 0,
            tournaments_played INTEGER DEFAULT 0,
            tournaments_won INTEGER DEFAULT 0,
            ranking_points INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS kingdoms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER UNIQUE NOT NULL,
            name TEXT DEFAULT 'Yangi Qirollik',
            flag TEXT DEFAULT '🏰',
            level INTEGER DEFAULT 1,
            gold INTEGER DEFAULT 0,
            population INTEGER DEFAULT 0,
            defense INTEGER DEFAULT 100,
            military_power INTEGER DEFAULT 0,
            FOREIGN KEY(owner_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS castle_upgrades (
            owner_id INTEGER PRIMARY KEY,
            level INTEGER DEFAULT 1,
            defense INTEGER DEFAULT 100,
            guards INTEGER DEFAULT 10,
            treasury_capacity INTEGER DEFAULT 10000,
            FOREIGN KEY(owner_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS armies (
            owner_id INTEGER PRIMARY KEY,
            soldiers INTEGER DEFAULT 0,
            archers INTEGER DEFAULT 0,
            guards INTEGER DEFAULT 0,
            cavalry INTEGER DEFAULT 0,
            special_units INTEGER DEFAULT 0,
            FOREIGN KEY(owner_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS territories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER,
            name TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            income INTEGER DEFAULT 0,
            defense INTEGER DEFAULT 100,
            strategic_value INTEGER DEFAULT 1,
            FOREIGN KEY(owner_id) REFERENCES users(user_id) ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS royal_positions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kingdom_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            position_key TEXT NOT NULL,
            appointed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(kingdom_id, position_key),
            FOREIGN KEY(kingdom_id) REFERENCES kingdoms(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            quantity INTEGER DEFAULT 0,
            UNIQUE(user_id, item_key),
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            flag TEXT DEFAULT '🏴',
            description TEXT DEFAULT '',
            leader_id INTEGER NOT NULL,
            level INTEGER DEFAULT 1,
            treasury INTEGER DEFAULT 0,
            power INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(leader_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS clan_members (
            clan_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            clan_role TEXT DEFAULT 'member',
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(clan_id, user_id),
            FOREIGN KEY(clan_id) REFERENCES clans(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS clan_wars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clan1_id INTEGER NOT NULL,
            clan2_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            winner_clan_id INTEGER,
            started_at TEXT,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS families (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user1_id INTEGER NOT NULL,
            user2_id INTEGER NOT NULL,
            marriage_date TEXT DEFAULT CURRENT_TIMESTAMP,
            family_level INTEGER DEFAULT 1,
            family_gold INTEGER DEFAULT 0,
            UNIQUE(user1_id, user2_id)
        );

        CREATE TABLE IF NOT EXISTS family_proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS daily_rewards (
            user_id INTEGER PRIMARY KEY,
            last_claim TEXT,
            streak INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS transfers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            currency TEXT NOT NULL,
            amount INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            gift_key TEXT NOT NULL,
            amount INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS market_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_key TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            price_gold INTEGER DEFAULT 0,
            price_coin INTEGER DEFAULT 0,
            price_diamond INTEGER DEFAULT 0,
            stock INTEGER DEFAULT -1,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            item_key TEXT NOT NULL,
            currency TEXT NOT NULL,
            price INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS black_market (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_key TEXT NOT NULL,
            name TEXT NOT NULL,
            price_diamond INTEGER DEFAULT 0,
            stock INTEGER DEFAULT 1,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS elite_purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            duration_days INTEGER NOT NULL,
            amount INTEGER DEFAULT 0,
            currency TEXT DEFAULT 'USD',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            creator_id INTEGER NOT NULL,
            status TEXT DEFAULT 'lobby',
            phase TEXT DEFAULT 'lobby',
            min_players INTEGER DEFAULT 7,
            max_players INTEGER DEFAULT 35,
            current_day INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            started_at TEXT,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS game_players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role_key TEXT,
            side TEXT,
            alive INTEGER DEFAULT 1,
            eliminated INTEGER DEFAULT 0,
            joined_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_id, user_id),
            FOREIGN KEY(game_id) REFERENCES games(id) ON DELETE CASCADE,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS game_actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            actor_id INTEGER NOT NULL,
            target_id INTEGER,
            action_type TEXT NOT NULL,
            value TEXT,
            round_number INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS game_votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER NOT NULL,
            voter_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            round_number INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(game_id, voter_id, round_number)
        );

        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id INTEGER UNIQUE NOT NULL,
            winning_side TEXT,
            winner_user_id INTEGER,
            result_text TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS duels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            challenger_id INTEGER NOT NULL,
            opponent_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            winner_id INTEGER,
            stake_gold INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            tournament_type TEXT DEFAULT 'solo',
            status TEXT DEFAULT 'registration',
            prize_gold INTEGER DEFAULT 0,
            prize_coin INTEGER DEFAULT 0,
            prize_diamond INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            started_at TEXT,
            ended_at TEXT
        );

        CREATE TABLE IF NOT EXISTS tournament_players (
            tournament_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            score INTEGER DEFAULT 0,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0,
            PRIMARY KEY(tournament_id, user_id)
        );

        CREATE TABLE IF NOT EXISTS ranking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            points INTEGER NOT NULL,
            reason TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS channel_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_type TEXT NOT NULL,
            content TEXT NOT NULL,
            posted INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS chat_settings (
            chat_id INTEGER PRIMARY KEY,
            setting_key TEXT NOT NULL,
            setting_value TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS mini_profiles (
            user_id INTEGER PRIMARY KEY,
            character_key TEXT,
            level INTEGER DEFAULT 1,
            background_key TEXT,
            clothing_key TEXT,
            weapon_key TEXT,
            horse_key TEXT,
            online INTEGER DEFAULT 0,
            last_seen TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS friends (
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(user_id, friend_id)
        );

        CREATE TABLE IF NOT EXISTS inactivity (
            user_id INTEGER PRIMARY KEY,
            last_activity TEXT DEFAULT CURRENT_TIMESTAMP,
            warning_sent INTEGER DEFAULT 0,
            removed INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS ai_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS system_settings (
            setting_key TEXT PRIMARY KEY,
            setting_value TEXT DEFAULT ''
        );

        CREATE INDEX IF NOT EXISTS idx_game_players_game
        ON game_players(game_id);

        CREATE INDEX IF NOT EXISTS idx_game_players_user
        ON game_players(user_id);

        CREATE INDEX IF NOT EXISTS idx_game_actions_game
        ON game_actions(game_id);

        CREATE INDEX IF NOT EXISTS idx_game_votes_game
        ON game_votes(game_id);

        CREATE INDEX IF NOT EXISTS idx_clan_members_user
        ON clan_members(user_id);

        CREATE INDEX IF NOT EXISTS idx_family_sender
        ON family_proposals(sender_id);

        CREATE INDEX IF NOT EXISTS idx_family_receiver
        ON family_proposals(receiver_id);

        CREATE INDEX IF NOT EXISTS idx_security_user
        ON security_logs(user_id);

        CREATE INDEX IF NOT EXISTS idx_ranking_user
        ON ranking_history(user_id);
        """)

        await db.commit()

    finally:
        await db.close()


# =========================
# GENERIC HELPERS
# =========================

async def fetchone(query: str, params=()):
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        return await cursor.fetchone()
    finally:
        await db.close()


async def fetchall(query: str, params=()):
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        return await cursor.fetchall()
    finally:
        await db.close()


async def execute(query: str, params=()):
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


# =========================
# USERS
# =========================

async def get_user(user_id: int):
    return await fetchone(
        "SELECT * FROM users WHERE user_id = ?",
        (user_id,)
    )


async def create_user(
    user_id: int,
    username: str = "",
    full_name: str = ""
):
    db = await get_db()
    try:
        await db.execute("""
            INSERT OR IGNORE INTO users
            (user_id, username, full_name)
            VALUES (?, ?, ?)
        """, (user_id, username, full_name))

        await db.execute("""
            INSERT OR IGNORE INTO settings (user_id)
            VALUES (?)
        """, (user_id,))

        await db.execute("""
            INSERT OR IGNORE INTO player_stats (user_id)
            VALUES (?)
        """, (user_id,))

        await db.execute("""
            INSERT OR IGNORE INTO mini_profiles (user_id)
            VALUES (?)
        """, (user_id,))

        await db.execute("""
            INSERT OR IGNORE INTO inactivity (user_id)
            VALUES (?)
        """, (user_id,))

        await db.commit()
    finally:
        await db.close()


async def update_user_info(
    user_id: int,
    username: str = "",
    full_name: str = ""
):
    await execute("""
        UPDATE users
        SET username = ?,
            full_name = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (username, full_name, user_id))


# =========================
# ECONOMY
# =========================

async def get_balance(user_id: int):
    row = await get_user(user_id)

    if row is None:
        return {
            "gold": 0,
            "coin": 0,
            "diamond": 0
        }

    return {
        "gold": row["gold"],
        "coin": row["coin"],
        "diamond": row["diamond"]
    }


async def update_balance(
    user_id: int,
    gold: int = 0,
    coin: int = 0,
    diamond: int = 0
):
    await execute("""
        UPDATE users
        SET gold = gold + ?,
            coin = coin + ?,
            diamond = diamond + ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE user_id = ?
    """, (gold, coin, diamond, user_id))


async def spend_balance(
    user_id: int,
    currency: str,
    amount: int
):
    if amount <= 0:
        return False

    if currency not in ("gold", "coin", "diamond"):
        return False

    db = await get_db()

    try:
        cursor = await db.execute(f"""
            UPDATE users
            SET {currency} = {currency} - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
              AND {currency} >= ?
        """, (amount, user_id, amount))

        await db.commit()
        return cursor.rowcount == 1

    finally:
        await db.close()


# =========================
# KINGDOM
# =========================

async def get_kingdom(user_id: int):
    return await fetchone(
        "SELECT * FROM kingdoms WHERE owner_id = ?",
        (user_id,)
    )


async def create_kingdom(
    user_id: int,
    name: str = "Yangi Qirollik",
    flag: str = "🏰"
):
    db = await get_db()

    try:
        await db.execute("""
            INSERT OR IGNORE INTO kingdoms
            (owner_id, name, flag)
            VALUES (?, ?, ?)
        """, (user_id, name, flag))

        await db.execute("""
            INSERT OR IGNORE INTO castle_upgrades
            (owner_id)
            VALUES (?)
        """, (user_id,))

        await db.execute("""
            INSERT OR IGNORE INTO armies
            (owner_id)
            VALUES (?)
        """, (user_id,))

        await db.commit()

    finally:
        await db.close()


async def get_castle(user_id: int):
    return await fetchone(
        "SELECT * FROM castle_upgrades WHERE owner_id = ?",
        (user_id,)
    )


async def get_army(user_id: int):
    return await fetchone(
        "SELECT * FROM armies WHERE owner_id = ?",
        (user_id,)
    )


# =========
# =========================
# GAME
# =========================

async def get_active_game(chat_id: int):
    return await fetchone("""
        SELECT *
        FROM games
        WHERE chat_id = ?
          AND status IN ('lobby', 'running')
        ORDER BY id DESC
        LIMIT 1
    """, (chat_id,))


async def create_game(
    chat_id: int,
    creator_id: int,
    min_players: int = 7,
    max_players: int = 35
):
    return await execute("""
        INSERT INTO games
        (chat_id, creator_id, status, phase, min_players, max_players)
        VALUES (?, ?, 'lobby', 'lobby', ?, ?)
    """, (chat_id, creator_id, min_players, max_players))


async def add_game_player(
    game_id: int,
    user_id: int
):
    await execute("""
        INSERT OR IGNORE INTO game_players
        (game_id, user_id)
        VALUES (?, ?)
    """, (game_id, user_id))


async def remove_game_player(
    game_id: int,
    user_id: int
):
    await execute("""
        DELETE FROM game_players
        WHERE game_id = ?
          AND user_id = ?
    """, (game_id, user_id))


async def get_game_players(game_id: int):
    return await fetchall("""
        SELECT
            gp.*,
            u.username,
            u.full_name,
            u.nickname
        FROM game_players gp
        JOIN users u
          ON u.user_id = gp.user_id
        WHERE gp.game_id = ?
        ORDER BY gp.id ASC
    """, (game_id,))


async def set_game_status(
    game_id: int,
    status: str,
    phase: Optional[str] = None
):
    if phase is None:
        await execute("""
            UPDATE games
            SET status = ?
            WHERE id = ?
        """, (status, game_id))
    else:
        await execute("""
            UPDATE games
            SET status = ?,
                phase = ?
            WHERE id = ?
        """, (status, phase, game_id))


async def assign_game_role(
    game_id: int,
    user_id: int,
    role_key: str,
    side: str
):
    await execute("""
        UPDATE game_players
        SET role_key = ?,
            side = ?
        WHERE game_id = ?
          AND user_id = ?
    """, (role_key, side, game_id, user_id))


async def eliminate_game_player(
    game_id: int,
    user_id: int
):
    await execute("""
        UPDATE game_players
        SET alive = 0,
            eliminated = 1
        WHERE game_id = ?
          AND user_id = ?
    """, (game_id, user_id))


async def add_game_action(
    game_id: int,
    actor_id: int,
    target_id: Optional[int],
    action_type: str,
    value: str = "",
    round_number: int = 0
):
    return await execute("""
        INSERT INTO game_actions
        (game_id, actor_id, target_id, action_type, value, round_number)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        game_id,
        actor_id,
        target_id,
        action_type,
        value,
        round_number
    ))


async def get_game_actions(
    game_id: int,
    round_number: Optional[int] = None
):
    if round_number is None:
        return await fetchall("""
            SELECT *
            FROM game_actions
            WHERE game_id = ?
            ORDER BY id ASC
        """, (game_id,))

    return await fetchall("""
        SELECT *
        FROM game_actions
        WHERE game_id = ?
          AND round_number = ?
        ORDER BY id ASC
    """, (game_id, round_number))


async def add_game_vote(
    game_id: int,
    voter_id: int,
    target_id: int,
    round_number: int = 0
):
    return await execute("""
        INSERT OR REPLACE INTO game_votes
        (game_id, voter_id, target_id, round_number)
        VALUES (?, ?, ?, ?)
    """, (
        game_id,
        voter_id,
        target_id,
        round_number
    ))


async def get_game_votes(
    game_id: int,
    round_number: Optional[int] = None
):
    if round_number is None:
        return await fetchall("""
            SELECT *
            FROM game_votes
            WHERE game_id = ?
            ORDER BY id ASC
        """, (game_id,))

    return await fetchall("""
        SELECT *
        FROM game_votes
        WHERE game_id = ?
          AND round_number = ?
        ORDER BY id ASC
    """, (game_id, round_number))


async def clear_game_votes(
    game_id: int,
    round_number: Optional[int] = None
):
    if round_number is None:
        await execute("""
            DELETE FROM game_votes
            WHERE game_id = ?
        """, (game_id,))
    else:
        await execute("""
            DELETE FROM game_votes
            WHERE game_id = ?
              AND round_number = ?
        """, (game_id, round_number))


async def save_game_result(
    game_id: int,
    winning_side: str,
    winner_user_id: Optional[int] = None,
    result_text: str = ""
):
    await execute("""
        INSERT OR REPLACE INTO game_results
        (game_id, winning_side, winner_user_id, result_text)
        VALUES (?, ?, ?, ?)
    """, (
        game_id,
        winning_side,
        winner_user_id,
        result_text
    ))

    await execute("""
        UPDATE games
        SET status = 'finished',
            phase = 'finished',
            ended_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (game_id,))


# =========================
# SECURITY
# =========================

async def security_log(
    user_id: Optional[int],
    action: str,
    details: str = ""
):
    return await execute("""
        INSERT INTO security_logs
        (user_id, action, details)
        VALUES (?, ?, ?)
    """, (user_id, action, details))


# =========================
# FAMILY
# =========================

async def get_family(user_id: int):
    return await fetchone("""
        SELECT *
        FROM families
        WHERE user1_id = ?
           OR user2_id = ?
        LIMIT 1
    """, (user_id, user_id))


async def create_family(
    user1_id: int,
    user2_id: int
):
    return await execute("""
        INSERT INTO families
        (user1_id, user2_id)
        VALUES (?, ?)
    """, (user1_id, user2_id))


async def get_pending_family_proposal(
    sender_id: int,
    receiver_id: int
):
    return await fetchone("""
        SELECT *
        FROM family_proposals
        WHERE sender_id = ?
          AND receiver_id = ?
          AND status = 'pending'
        ORDER BY id DESC
        LIMIT 1
    """, (sender_id, receiver_id))


async def create_family_proposal(
    sender_id: int,
    receiver_id: int
):
    return await execute("""
        INSERT INTO family_proposals
        (sender_id, receiver_id, status)
        VALUES (?, ?, 'pending')
    """, (sender_id, receiver_id))


async def update_family_proposal(
    proposal_id: int,
    status: str
):
    await execute("""
        UPDATE family_proposals
        SET status = ?
        WHERE id = ?
    """, (status, proposal_id))


# =========================
# INVENTORY
# =========================

async def get_inventory(user_id: int):
    return await fetchall("""
        SELECT *
        FROM inventory
        WHERE user_id = ?
        ORDER BY id ASC
    """, (user_id,))


async def add_inventory_item(
    user_id: int,
    item_key: str,
    quantity: int = 1
):
    if quantity <= 0:
        return False

    await execute("""
        INSERT INTO inventory
        (user_id, item_key, quantity)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, item_key)
        DO UPDATE SET quantity = quantity + excluded.quantity
    """, (user_id, item_key, quantity))

    return True


async def remove_inventory_item(
    user_id: int,
    item_key: str,
    quantity: int = 1
):
    if quantity <= 0:
        return False

    db = await get_db()

    try:
        cursor = await db.execute("""
            UPDATE inventory
            SET quantity = quantity - ?
            WHERE user_id = ?
              AND item_key = ?
              AND quantity >= ?
        """, (
            quantity,
            user_id,
            item_key,
            quantity
        ))

        await db.commit()

        if cursor.rowcount != 1:
            return False

        await db.execute("""
            DELETE FROM inventory
            WHERE user_id = ?
              AND item_key = ?
              AND quantity <= 0
        """, (user_id, item_key))

        await db.commit()

        return True

    finally:
        await db.close()


# =========================
# RANKING
# =========================

async def get_top_players(limit: int = 20):
    return await fetchall("""
        SELECT
            u.user_id,
            u.username,
            u.full_name,
            u.nickname,
            u.level,
            ps.games_won,
            ps.ranking_points
        FROM users u
        JOIN player_stats ps
          ON ps.user_id = u.user_id
        ORDER BY ps.ranking_points DESC,
                 ps.games_won DESC,
                 u.level DESC
        LIMIT ?
    """, (limit,))


async def add_ranking_points(
    user_id: int,
    points: int,
    reason: str = ""
):
    if points == 0:
        return

    await execute("""
        UPDATE player_stats
        SET ranking_points = ranking_points + ?
        WHERE user_id = ?
    """, (points, user_id))

    await execute("""
        INSERT INTO ranking_history
        (user_id, points, reason)
        VALUES (?, ?, ?)
    """, (user_id, points, reason))


# =========================
# DAILY REWARD
# =========================

async def get_daily_reward(user_id: int):
    return await fetchone("""
        SELECT *
        FROM daily_rewards
        WHERE user_id = ?
    """, (user_id,))


async def set_daily_reward(
    user_id: int,
    last_claim: str,
    streak: int
):
    await execute("""
        INSERT INTO daily_rewards
        (user_id, last_claim, streak)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            last_claim = excluded.last_claim,
            streak = excluded.streak
    """, (user_id, last_claim, streak))


# =========================
# PLAYER STATS
# =========================

async def update_player_stats(
    user_id: int,
    games_played: int = 0,
    games_won: int = 0,
    games_lost: int = 0,
    kills: int = 0,
    deaths: int = 0
):
    await execute("""
        UPDATE player_stats
        SET games_played = games_played + ?,
            games_won = games_won + ?,
            games_lost = games_lost + ?,
            kills = kills + ?,
            deaths = deaths + ?
        WHERE user_id = ?
    """, (
        games_played,
        games_won,
        games_lost,
        kills,
        deaths,
        user_id
    ))


# =========================
# MINI PROFILE
# =========================

async def get_mini_profile(user_id: int):
    return await fetchone("""
        SELECT *
        FROM mini_profiles
        WHERE user_id = ?
    """, (user_id,))


async def update_mini_profile(
    user_id: int,
    character_key: Optional[str] = None,
    background_key: Optional[str] = None,
    clothing_key: Optional[str] = None,
    weapon_key: Optional[str] = None,
    horse_key: Optional[str] = None
):
    await execute("""
        UPDATE mini_profiles
        SET character_key = COALESCE(?, character_key),
            background_key = COALESCE(?, background_key),
            clothing_key = COALESCE(?, clothing_key),
            weapon_key = COALESCE(?, weapon_key),
            horse_key = COALESCE(?, horse_key)
        WHERE user_id = ?
    """, (
        character_key,
        background_key,
        clothing_key,
        weapon_key,
        horse_key,
        user_id
    ))


# =========================
# INACTIVITY
# =========================

async def update_activity(user_id: int):
    await execute("""
        INSERT INTO inactivity
        (user_id, last_activity, warning_sent, removed)
        VALUES (?, CURRENT_TIMESTAMP, 0, 0)
        ON CONFLICT(user_id)
        DO UPDATE SET
            last_activity = CURRENT_TIMESTAMP,
            warning_sent = 0,
            removed = 0
    """, (user_id,))


async def get_inactivity(user_id: int):
    return await fetchone("""
        SELECT *
        FROM inactivity
        WHERE user_id = ?
    """, (user_id,))
