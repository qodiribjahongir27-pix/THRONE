import aiosqlite
from typing import Optional, Any


DB_NAME = "throne.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

async def get_db():
    db = await aiosqlite.connect(DB_NAME)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    return db


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

async def init_db():
    db = await get_db()

    try:
        # ----------------------------------------------------
        # USERS
        # ----------------------------------------------------
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

                is_banned INTEGER DEFAULT 0,
                is_active INTEGER DEFAULT 1,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # ----------------------------------------------------
        # USER SETTINGS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                user_id INTEGER PRIMARY KEY,

                notifications INTEGER DEFAULT 1,
                private_messages INTEGER DEFAULT 1,
                sound INTEGER DEFAULT 1,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # PLAYER STATS
        # ----------------------------------------------------
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

                tournaments INTEGER DEFAULT 0,
                tournament_wins INTEGER DEFAULT 0,

                rating INTEGER DEFAULT 0,

                gold_earned INTEGER DEFAULT 0,
                gold_spent INTEGER DEFAULT 0,

                coin_earned INTEGER DEFAULT 0,
                diamond_earned INTEGER DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # KINGDOMS
        # ----------------------------------------------------
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
                military_power INTEGER DEFAULT 0,

                prestige INTEGER DEFAULT 0,

                treasury_capacity INTEGER DEFAULT 1000,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # CASTLE UPGRADES
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS castle_upgrades (
                user_id INTEGER PRIMARY KEY,

                walls INTEGER DEFAULT 1,
                gate INTEGER DEFAULT 1,
                barracks INTEGER DEFAULT 1,
                treasury INTEGER DEFAULT 1,
                throne_room INTEGER DEFAULT 1,
                watchtower INTEGER DEFAULT 1,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # ARMY
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS armies (
                user_id INTEGER PRIMARY KEY,

                soldiers INTEGER DEFAULT 0,
                archers INTEGER DEFAULT 0,
                guards INTEGER DEFAULT 0,
                cavalry INTEGER DEFAULT 0,

                elite_units INTEGER DEFAULT 0,

                attack_power INTEGER DEFAULT 0,
                defense_power INTEGER DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # TERRITORIES
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS territories (
                territory_id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT UNIQUE NOT NULL,

                owner_id INTEGER,

                income INTEGER DEFAULT 0,
                defense_required INTEGER DEFAULT 0,
                strategic_value INTEGER DEFAULT 0,

                status TEXT DEFAULT 'neutral',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (owner_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            )
        """)

        # ----------------------------------------------------
        # ROYAL POSITIONS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS royal_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                kingdom_owner_id INTEGER NOT NULL,

                position_key TEXT NOT NULL,

                player_id INTEGER,

                appointed_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE (
                    kingdom_owner_id,
                    position_key
                ),

                FOREIGN KEY (kingdom_owner_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (player_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            )
        """)

        # ----------------------------------------------------
        # INVENTORY
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,

                item_type TEXT DEFAULT 'item',

                quantity INTEGER DEFAULT 1,

                level INTEGER DEFAULT 1,

                equipped INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE (
                    user_id,
                    item_key
                ),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # CLANS
        # ----------------------------------------------------
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

                rating INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (leader_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # CLAN MEMBERS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clan_members (
                clan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                clan_role TEXT DEFAULT 'member',

                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (
                    clan_id,
                    user_id
                ),

                FOREIGN KEY (clan_id)
                    REFERENCES clans(clan_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # CLAN WARS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clan_wars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                attacker_clan_id INTEGER NOT NULL,
                defender_clan_id INTEGER NOT NULL,

                status TEXT DEFAULT 'preparation',

                attacker_score INTEGER DEFAULT 0,
                defender_score INTEGER DEFAULT 0,

                winner_clan_id INTEGER,

                started_at TEXT,
                finished_at TEXT,

                FOREIGN KEY (attacker_clan_id)
                    REFERENCES clans(clan_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (defender_clan_id)
                    REFERENCES clans(clan_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (winner_clan_id)
                    REFERENCES clans(clan_id)
                    ON DELETE SET NULL
            )
        """)

        # ----------------------------------------------------
        # FAMILIES
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,

                married_at TEXT DEFAULT CURRENT_TIMESTAMP,

                level INTEGER DEFAULT 1,
                family_gold INTEGER DEFAULT 0,

                UNIQUE (
                    user1_id,
                    user2_id
                ),

                FOREIGN KEY (user1_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user2_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # FAMILY PROPOSALS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS family_proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                status TEXT DEFAULT 'pending',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # DAILY REWARDS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id INTEGER PRIMARY KEY,

                last_claim TEXT,

                streak INTEGER DEFAULT 0,

                total_claims INTEGER DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # TRANSFERS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                currency TEXT NOT NULL,
                amount INTEGER NOT NULL,

                transfer_type TEXT DEFAULT 'transfer',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # GIFTS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS gifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,

                gift_key TEXT NOT NULL,
                gift_name TEXT NOT NULL,

                price INTEGER DEFAULT 0,
                currency TEXT DEFAULT 'gold',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (sender_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (receiver_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # MARKET
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS market_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                seller_id INTEGER NOT NULL,

                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,

                quantity INTEGER DEFAULT 1,

                price INTEGER NOT NULL,
                currency TEXT DEFAULT 'gold',

                status TEXT DEFAULT 'active',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (seller_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # PURCHASE HISTORY
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,

                quantity INTEGER DEFAULT 1,

                price INTEGER NOT NULL,
                currency TEXT NOT NULL,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # BLACK MARKET
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS black_market (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_key TEXT NOT NULL,
                item_name TEXT NOT NULL,

                price INTEGER NOT NULL,
                currency TEXT DEFAULT 'diamond',

                quantity INTEGER DEFAULT 1,

                available INTEGER DEFAULT 1,

                expires_at TEXT
            )
        """)

        # ----------------------------------------------------
        # ELITE PURCHASES
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS elite_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                duration_days INTEGER NOT NULL,

                price REAL NOT NULL,

                currency TEXT DEFAULT 'USD',

                payment_id TEXT,

                status TEXT DEFAULT 'pending',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # GAMES
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS games (
                game_id INTEGER PRIMARY KEY AUTOINCREMENT,

                chat_id INTEGER NOT NULL,

                status TEXT DEFAULT 'lobby',
                phase TEXT DEFAULT 'lobby',

                day_number INTEGER DEFAULT 0,

                min_players INTEGER DEFAULT 5,

                max_players INTEGER DEFAULT 35,

                lobby_message_id INTEGER,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,
                finished_at TEXT
            )
        """)

        # ----------------------------------------------------
        # GAME PLAYERS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_players (
                game_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                role_key TEXT,

                alive INTEGER DEFAULT 1,

                protected INTEGER DEFAULT 0,
                blocked INTEGER DEFAULT 0,
                poisoned INTEGER DEFAULT 0,

                last_words TEXT DEFAULT '',

                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (
                    game_id,
                    user_id
                ),

                FOREIGN KEY (game_id)
                    REFERENCES games(game_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        # ----------------------------------------------------
        # GAME ACTIONS
        # ----------------------------------------------------
        await db.execute("""
            CREATE TABLE IF NOT EXISTS game_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,

                actor_id INTEGER NOT NULL,
                target_id INTEG
