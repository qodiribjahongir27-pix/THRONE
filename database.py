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
    await db.execute("PRAGMA journal_mode = WAL")
    await db.execute("PRAGMA busy_timeout = 5000")

    return db


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

async def init_db():
    db = await get_db()

    try:
        await db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT DEFAULT '',
                full_name TEXT DEFAULT 'O‘yinchi',
                nickname TEXT DEFAULT '',
                flag TEXT DEFAULT '🏴',

                gold INTEGER DEFAULT 0,
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
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS player_stats (
                user_id INTEGER PRIMARY KEY,

                games_played INTEGER DEFAULT 0,
                games_won INTEGER DEFAULT 0,
                games_lost INTEGER DEFAULT 0,

                kills INTEGER DEFAULT 0,
                deaths INTEGER DEFAULT 0,

                duel_played INTEGER DEFAULT 0,
                duel_wins INTEGER DEFAULT 0,

                tournament_played INTEGER DEFAULT 0,
                tournament_wins INTEGER DEFAULT 0,

                ranking_points INTEGER DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS kingdoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER UNIQUE NOT NULL,

                name TEXT DEFAULT 'Yangi Qirollik',
                flag TEXT DEFAULT '🏴',

                level INTEGER DEFAULT 1,
                gold INTEGER DEFAULT 0,
                population INTEGER DEFAULT 0,
                defense INTEGER DEFAULT 0,
                military_power INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (owner_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS castle_upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER UNIQUE NOT NULL,

                level INTEGER DEFAULT 1,
                defense INTEGER DEFAULT 100,
                guards INTEGER DEFAULT 10,
                treasury_capacity INTEGER DEFAULT 1000,

                FOREIGN KEY (owner_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS armies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER UNIQUE NOT NULL,

                soldiers INTEGER DEFAULT 0,
                archers INTEGER DEFAULT 0,
                guards INTEGER DEFAULT 0,
                cavalry INTEGER DEFAULT 0,
                special_units INTEGER DEFAULT 0,

                FOREIGN KEY (owner_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS territories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                kingdom_id INTEGER,
                name TEXT NOT NULL,
                income INTEGER DEFAULT 0,
                strategic_value INTEGER DEFAULT 0,
                defense_required INTEGER DEFAULT 0,

                owner_type TEXT DEFAULT 'neutral',
                owner_id INTEGER,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS royal_positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                kingdom_id INTEGER NOT NULL,
                position TEXT NOT NULL,
                user_id INTEGER,

                UNIQUE(kingdom_id, position),

                FOREIGN KEY (kingdom_id)
                    REFERENCES kingdoms(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE SET NULL
            );


            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                item_key TEXT NOT NULL,
                item_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 0,

                UNIQUE(user_id, item_key),

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS clans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                owner_id INTEGER NOT NULL,
                name TEXT UNIQUE NOT NULL,
                flag TEXT DEFAULT '🏴',
                description TEXT DEFAULT '',

                level INTEGER DEFAULT 1,
                experience INTEGER DEFAULT 0,
                power INTEGER DEFAULT 0,
                treasury INTEGER DEFAULT 0,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (owner_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS clan_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                clan_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT DEFAULT 'member',
                joined_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(clan_id, user_id),

                FOREIGN KEY (clan_id)
                    REFERENCES clans(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS clan_wars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                attacker_clan_id INTEGER NOT NULL,
                defender_clan_id INTEGER NOT NULL,

                status TEXT DEFAULT 'preparation',

                attacker_score INTEGER DEFAULT 0,
                defender_score INTEGER DEFAULT 0,

                winner_clan_id INTEGER,

                started_at TEXT DEFAULT CURRENT_TIMESTAMP,
                ended_at TEXT
            );


            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,

                family_level INTEGER DEFAULT 1,
                family_experience INTEGER DEFAULT 0,
                family_gold INTEGER DEFAULT 0,

                married_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user1_id, user2_id),

                FOREIGN KEY (user1_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user2_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


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
            );


            CREATE TABLE IF NOT EXISTS daily_rewards (
                user_id INTEGER PRIMARY KEY,

                last_claim TEXT,
                streak INTEGER DEFAULT 0,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
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
                gift_name TEXT DEFAULT '',
                quantity INTEGER DEFAULT 1,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS market_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_key TEXT UNIQUE NOT NULL,
                item_name TEXT NOT NULL,

                currency TEXT DEFAULT 'gold',
                price INTEGER DEFAULT 0,
                stock INTEGER DEFAULT -1,

                active INTEGER DEFAULT 1
            );


            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                item_key TEXT NOT NULL,

                currency TEXT NOT NULL,
                amount INTEGER NOT NULL,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS black_market (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                item_key TEXT UNIQUE NOT NULL,
                item_name TEXT NOT NULL,

                currency TEXT DEFAULT 'diamond',
                price INTEGER DEFAULT 0,

                active INTEGER DEFAULT 1
            );


            CREATE TABLE IF NOT EXISTS elite_purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                plan TEXT NOT NULL,
                amount REAL DEFAULT 0,
                currency TEXT DEFAULT 'USD',

                days INTEGER DEFAULT 30,
                status TEXT DEFAULT 'pending',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                chat_id INTEGER NOT NULL,
                creator_id INTEGER NOT NULL,

                status TEXT DEFAULT 'lobby',
                phase TEXT DEFAULT 'lobby',

                min_players INTEGER DEFAULT 5,
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

                FOREIGN KEY (game_id)
                    REFERENCES games(id)
                    ON DELETE CASCADE,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS game_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,
                actor_id INTEGER NOT NULL,
                target_id INTEGER,

                action_type TEXT NOT NULL,
                value TEXT DEFAULT '',

                round_number INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS game_votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,
                voter_id INTEGER NOT NULL,
                target_id INTEGER,

                round_number INTEGER DEFAULT 0,

                UNIQUE(game_id, voter_id, round_number)
            );


            CREATE TABLE IF NOT EXISTS game_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                game_id INTEGER NOT NULL,

                winning_side TEXT,
                winner_user_id INTEGER,

                result_text TEXT DEFAULT '',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS duels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                challenger_id INTEGER NOT NULL,
                opponent_id INTEGER NOT NULL,

                status TEXT DEFAULT 'pending',

                winner_id INTEGER,

                challenger_health INTEGER DEFAULT 100,
                opponent_health INTEGER DEFAULT 100,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                ended_at TEXT
            );


            CREATE TABLE IF NOT EXISTS duel_rounds (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                duel_id INTEGER NOT NULL,
                attacker_id INTEGER NOT NULL,
                defender_id INTEGER NOT NULL,

                damage INTEGER DEFAULT 0,
                round_number INTEGER DEFAULT 1,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS tournaments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                name TEXT NOT NULL,
                tournament_type TEXT DEFAULT 'solo',

                status TEXT DEFAULT 'registration',

                prize_gold INTEGER DEFAULT 0,
                prize_coin INTEGER DEFAULT 0,
                prize_diamond INTEGER DEFAULT 0,

                max_players INTEGER DEFAULT 32,

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                started_at TEXT,
                ended_at TEXT
            );


            CREATE TABLE IF NOT EXISTS tournament_players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                tournament_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,

                position INTEGER,
                score INTEGER DEFAULT 0,

                UNIQUE(tournament_id, user_id)
            );


            CREATE TABLE IF NOT EXISTS ranking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,

                category TEXT NOT NULL,
                points INTEGER DEFAULT 0,

                recorded_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS channel_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                channel_id INTEGER NOT NULL,
                message_id INTEGER,

                post_type TEXT DEFAULT '',
                content TEXT DEFAULT '',

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

                game_enabled INTEGER DEFAULT 1,
                auto_welcome INTEGER DEFAULT 1,
                language TEXT DEFAULT 'uz',

                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS mini_profiles (
                user_id INTEGER PRIMARY KEY,

                character_key TEXT,
                background_key TEXT,

                level INTEGER DEFAULT 1,

                clothing_key TEXT,
                weapon_key TEXT,
                horse_key TEXT,

                online INTEGER DEFAULT 0,
                last_seen TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS friends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER NOT NULL,
                friend_id INTEGER NOT NULL,

                status TEXT DEFAULT 'accepted',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP,

                UNIQUE(user_id, friend_id)
            );


            CREATE TABLE IF NOT EXISTS inactivity (
                user_id INTEGER PRIMARY KEY,

                last_activity TEXT,
                warning_sent INTEGER DEFAULT 0,
                removal_due TEXT,

                FOREIGN KEY (user_id)
                    REFERENCES users(user_id)
                    ON DELETE CASCADE
            );


            CREATE TABLE IF NOT EXISTS ai_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                user_id INTEGER,
                question TEXT DEFAULT '',
                answer TEXT DEFAULT '',

                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );


            CREATE TABLE IF NOT EXISTS system_settings (
                key TEXT PRIMARY KEY,
                value TEXT DEFAULT ''
            );


            CREATE INDEX IF NOT EXISTS idx_clan_members_clan
                ON clan_members(clan_id);

            CREATE INDEX IF NOT EXISTS idx_clan_members_user
                ON clan_members(user_id);

            CREATE INDEX IF NOT EXISTS idx_game_players_game
                ON game_players(game_id);

            CREATE INDEX IF NOT EXISTS idx_game_players_user
                ON game_players(user_id);

            CREATE INDEX IF NOT EXISTS idx_game_actions_game
                ON game_actions(game_id);

            CREATE INDEX IF NOT EXISTS idx_game_votes_game
                ON game_votes(game_id);

            CREATE INDEX IF NOT EXISTS idx_family_user1
                ON families(user1_id);

            CREATE INDEX IF NOT EXISTS idx_family_user2
                ON families(user2_id);

            CREATE INDEX IF NOT EXISTS idx_security_logs_user
                ON security_logs(user_id);

            CREATE INDEX IF NOT EXISTS idx_ranking_category
                ON ranking_history(category);

            CREATE INDEX IF NOT EXISTS idx_proposals_receiver
                ON family_proposals(receiver_id);

            CREATE INDEX IF NOT EXISTS idx_proposals_sender
                ON family_proposals(sender_id);
            """
        )

        await db.commit()

    finally:
        await db.clo
