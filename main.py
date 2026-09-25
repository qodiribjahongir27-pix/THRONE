import os
import sqlite3
import logging
from datetime import datetime, date

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# =========================================================
# THRONE CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Railway Variables ichiga o'zingizning Telegram ID'ingizni yozasiz.
CREATOR_ID = int(os.getenv("CREATOR_ID", "0"))

DB_FILE = "throne.db"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger("THRONE")


# =========================================================
# DATABASE
# =========================================================

def db():
    connection = sqlite3.connect(DB_FILE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = db()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT DEFAULT '',

            level INTEGER DEFAULT 1,
            xp INTEGER DEFAULT 0,

            gold INTEGER DEFAULT 1000,
            coin INTEGER DEFAULT 100,
            diamond INTEGER DEFAULT 10,

            elite INTEGER DEFAULT 0,

            kingdom TEXT DEFAULT 'Yangi Qirollik',
            position TEXT DEFAULT 'Fuqaro',

            power INTEGER DEFAULT 10,
            defense INTEGER DEFAULT 10,

            weapon TEXT DEFAULT 'Oddiy qilich',
            armor TEXT DEFAULT 'Oddiy zirh',
            horse INTEGER DEFAULT 0,

            avatar TEXT DEFAULT 'warrior',

            clan_id INTEGER DEFAULT NULL,
            spouse_id INTEGER DEFAULT NULL,

            last_bonus TEXT DEFAULT '',

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS games (
            chat_id INTEGER PRIMARY KEY,

            active INTEGER DEFAULT 0,

            started_by INTEGER DEFAULT 0,

            phase TEXT DEFAULT 'tayyorgarlik',

            turn INTEGER DEFAULT 0,

            started_at TEXT DEFAULT ''
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_players (
            chat_id INTEGER,
            user_id INTEGER,

            role TEXT DEFAULT 'Fuqaro',

            alive INTEGER DEFAULT 1,

            joined_at TEXT,

            PRIMARY KEY(chat_id, user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT UNIQUE,

            owner_id INTEGER,

            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            sender_id INTEGER,
            receiver_id INTEGER,

            item TEXT,

            amount INTEGER DEFAULT 1,

            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS duels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            challenger INTEGER,
            opponent INTEGER,

            winner INTEGER DEFAULT NULL,

            status TEXT DEFAULT 'pending',

            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournaments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT,

            status TEXT DEFAULT 'open',

            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tournament_players (
            tournament_id INTEGER,
            user_id INTEGER,

            PRIMARY KEY(tournament_id, user_id)
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# DATABASE HELPERS
# =========================================================

def get_player(user_id):

    connection = db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM players WHERE user_id = ?",
        (user_id,)
    )

    player = cursor.fetchone()

    connection.close()

    return player


def create_player(user):

    connection = db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT user_id FROM players WHERE user_id = ?",
        (user.id,)
    )

    exists = cursor.fetchone()

    if not exists:

        cursor.execute("""
            INSERT INTO players (
                user_id,
                name,
                username
            )
            VALUES (?, ?, ?)
        """, (
            user.id,
            user.first_name or "Player",
            user.username or ""
        ))

    else:

        cursor.execute("""
            UPDATE players
            SET
                name = ?,
                username = ?
            WHERE user_id = ?
        """, (
            user.first_name or "Player",
            user.username or "",
            user.id
        ))

    connection.commit()
    connection.close()


def update_player(user_id, **values):

    if not values:
        return

    connection = db()
    cursor = connection.cursor()

    fields = ", ".join(
        f"{key} = ?"
        for key in values.keys()
    )

    params = list(values.values())
    params.append(user_id)

    cursor.execute(
        f"""
        UPDATE players
        SET {fields}
        WHERE user_id = ?
        """,
        params
    )

    connection.commit()
    connection.close()


# =========================================================
# CREATOR SYSTEM
# =========================================================

def is_creator(user_id):

    return (
        CREATOR_ID != 0
        and user_id == CREATOR_ID
    )


def gold(player):

    if is_creator(player["user_id"]):
        return "∞"

    return f"{player['gold']:,}"


def coin(player):

    if is_creator(player["user_id"]):
        return "∞"

    return f"{player['coin']:,}"


def diamond(player):

    if is_creator(player["user_id"]):
        return "∞"

    return f"{player['diamond']:,}"


def elite(player):

    if is_creator(player["user_id"]):
        return "AKTIV ∞"

    if player["elite"]:
        return "AKTIV"

    return "FAOL EMAS"


# =========================================================
# ECONOMY
# =========================================================

def add_gold(user_id, amount):

    if is_creator(user_id):
        return

    connection = db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET gold = gold + ?
        WHERE user_id = ?
    """, (
        amount,
        user_id
    ))

    connection.commit()
    connection.close()


def spend_gold(user_id, amount):

    if is_creator(user_id):
        return True

    player = get_player(user_id)

    if not player:
        return False

    if player["gold"] < amount:
        return False

    connection = db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE players
        SET gold = gold - ?
        WHERE user_id = ?
    """, (
        amount,
        user_id
    ))

    connection.commit()
    connection.close()

    return True


# =========================================================
# XP / LEVEL
# =========================================================

def add_xp(user_id, amount):

    player = get_player(user_id)

    if not player:
        return

    xp = player["xp"] + amount
    level = player["level"]

    required = level * 100

    while xp >= required:

        xp -= required
        level += 1

        required = level * 100

    update_player(
        user_id,
        xp=xp,
        level=level
    )


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():

    return InlineKeyboardMarkup([

        [
            InlineKeyboardButton(
                "👑 Qirollik",
                callback_data="kingdom"
            ),

            InlineKeyboardButton(
                "👤 Profil",
                callback_data="profile"
            )
        ],

        [
            InlineKeyboardButton(
                "🎮 O‘yinlar",
                callback_data="games"
            ),

            InlineKeyboardButton(
                "🎒 Inventar",
                callback_data="inventory"
            )
        ],

        [
            InlineKeyboardButton(
                "💰 Bozor",
                callback_data="market"
            ),

            InlineKeyboardButton(
                "🏴 Klanlar",
                callback_data="clans"
            )
        ],

        [
            InlineKeyboardButton(
                "❤️ Oila",
                callback_data="family"
            ),

            InlineKeyboardButton(
                "📊 Reyting",
                callback_data="rating"
            )
        ],

        [
            InlineKeyboardButton(
                "🎁 Bonus",
                callback_data="bonus"
            ),

            InlineKeyboardButton(
                "🏆 Turnir",
                callback_data="tournament"
            )
        ],

        [
            InlineKeyboardButton(
                "⚔️ Duel",
                callback_data="duel"
            ),

            InlineKeyboardButton(
                "📖 Qoidalar",
                callback_data="rules"
            )
        ],

        [
            InlineKeyboardButton(
                "⚙️ Sozlamalar",
                callback_data="settings"
            )
        ]

    ])


def back_button():

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "⬅️ Bosh menyu",
                callback_data="home"
            )
        ]
    ])


# =========================================================
# LOBBY
# =========================================================

def lobby_text(player):

    if is_creator(player["user_id"]):

        return (
            "👑 THRONE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "𓆩 ELITE 𓆪 YARATUVCHI\n\n"

            f"👤 {player['name']}\n"
            f"⭐ Level {player['level']}  •  XP {player['xp']}\n\n"

            "💰 BOYLIK\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n\n"

            "⚜️ Elite Pass — AKTIV ∞\n\n"

            f"🏰 Qirollik: {player['kingdom']}\n"
            f"⚜️ Lavozim: {player['position']}\n\n"

            f"⚔️ Kuch: {player['power']}\n"
            f"🛡️ Mudofaa: {player['defense']}\n\n"

            "━━━━━━━━━━━━━━━━━━\n"
            "👑 Taxt seni kutmoqda."
        )

    return (
        "👑 THRONE\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"👤 {player['name']}\n"
        f"⭐ Level {player['level']}  •  XP {player['xp']}\n\n"

        "💰 BOYLIK\n"
        f"🟡 Oltin: {gold(player)}\n"
        f"🪙 Coin: {coin(player)}\n"
        f"💎 Olmos: {diamond(player)}\n\n"

        f"⚜️ Elite Pass — {elite(player)}\n\n"

        f"🏰 Qirollik: {player['kingdom']}\n"
        f"⚜️ Lavozim: {player['position']}\n\n"

        f"⚔️ Kuch: {player['power']}\n"
        f"🛡️ Mudofaa: {player['defense']}\n\n"

        "━━━━━━━━━━━━━━━━━━\n"
        "⚔️ Taxt uchun kurash boshlanadi."
    )


# =========================================================
# /START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    create_player(user)

    player = get_player(user.id)

    if update.effective_chat.type in (
        "group",
        "supergroup"
    ):

        await update.message.reply_text(
            "👑 THRONE\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "🏰 QIROLLIK GURUHGA TAYYOR\n\n"

            "⚔️ O‘yinni boshlash uchun "
            "guruh administratori:\n\n"

            "/startgame\n\n"

            "👥 O‘yinga kirish:\n"
            "/join\n\n"

            "📖 Qoidalar:\n"
            "/rules"
        )

        return

    await update.message.reply_text(
        lobby_text(player),
        reply_markup=main_menu()
    )


# =========================================================
# PROFILE
# =========================================================

async def profile_command(update, context):

    create_player(update.effective_user)

    player = get_player(
        update.effective_user.id
    )

    await update.message.reply_text(
        lobby_text(player),
        reply_markup=main_menu()
    )


# =========================================================
# GROUP GAME
# =========================================================

async def start_game(update, context):

    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in (
        "group",
        "supergroup"
    ):

        await update.message.reply_text(
            "⛔ Bu buyruq faqat guruhda ishlaydi."
        )

        return

    member = await context.bot.get_chat_member(
        chat.id,
        user.id
    )

    if member.status not in (
        "administrator",
        "creator"
    ):

        await update.message.reply_text(
            "⛔ O‘yinni faqat guruh administratori boshlashi mumkin."
        )

        return

    connection = db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM games WHERE chat_id = ?",
        (chat.id,)
    )

    game = cursor.fetchone()

    if game and game["active"]:

        await update.message.reply_text(
            "⚔️ O‘yin allaqachon davom etmoqda.\n\n"
            "/join orqali qo‘shiling."
        )

        connection.close()

        return

    cursor.execute("""
        INSERT OR REPLACE INTO games (
            chat_id,
            active,
            started_by,
            phase,
            turn,
            started_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        chat.id,
        1,
        user.id,
        "tayyorgarlik",
        0,
        datetime.utcnow().isoformat()
    ))

    connection.commit()
    connection.close()

    await update.message.reply_text(
        "👑 THRONE — O‘YIN BOSHLANDI\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "🏰 Yangi qirollik taqdiri boshlandi.\n\n"

        "👥 O‘yinga kirish:\n"
        "/join\n\n"

        "⏳ Bosqich: TAYYORGARLIK\n\n"

        "⚔️ Taxt uchun kurash boshlanmoqda."
    )


async def join_game(update, context):

    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in (
        "group",
        "supergroup"
    ):

        await update.message.reply_text(
            "⛔ /join faqat guruhda ishlaydi."
        )

        return

    create_player(user)

    connection = db()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM games WHERE chat_id = ?",
        (chat.id,)
    )

    game = cursor.fetchone()

    if not game or not game["active"]:

        await update.message.reply_text(
            "❌ Hozir faol o‘yin yo‘q."
        )

        connection.close()

        return

    cursor.execute("""
        INSERT OR IGNORE INTO game_players (
            chat_id,
            user_id,
            role,
            alive,
            joined_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        chat.id,
        user.id,
        "Fuqaro",
        1,
        datetime.utcnow().isoformat()
    ))

    connection.commit()

    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM game_players
        WHERE chat_id = ?
    """, (chat.id,))

    total = cursor.fetchone()["total"]

    connection.close()

    await update.message.reply_text(
        f"👤 {user.first_name} o‘yinga qo‘shildi.\n\n"
        f"👥 Ishtirokchilar: {total}"
    )


async def stop_game(update, context):

    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in (
        "group",
        "supergroup"
    ):

        return

    member = await context.bot.get_chat_member(
        chat.id,
        user.id
    )

    if member.status not in (
        "administrator",
        "creator"
    ):

        await update.message.reply_text(
            "⛔ Faqat admin."
        )

        return

    connection = db()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE games
        SET active = 0,
            phase = 'yakunlangan'
        WHERE chat_id = ?
    """, (chat.id,))

    connection.commit()
    connection.close()

    await update.message.reply_text(
        "🛑 THRONE o‘yini to‘xtatildi."
    )


# =========================================================
# RULES
# =========================================================

async def rules_command(update, context):

    await update.message.reply_text(
        "📖 THRONE QOIDALARI\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        "1️⃣ Guruh o‘yinini faqat admin boshlaydi.\n\n"

        "2️⃣ Har bir o‘yinchi o‘z qarorini qabul qiladi.\n\n"

        "3️⃣ Resurslar server tomonidan boshqariladi.\n\n"

        "4️⃣ O‘yin ichidagi noqonuniy manipulyatsiya taqiqlanadi.\n\n"

        "5️⃣ Botni buzishga yoki soxta so‘rov yuborishga "
        "urinishlar bloklanadi.\n\n"

        "6️⃣ Mini App profil, avatar, inventar va "
        "vizual qirollik interfeysi uchun ishlatiladi."
    )


# =========================================================
# CALLBACK PAGES
# =========================================================

def page_text(key, player):

    if key == "kingdom":

        return (
            "👑 QIROLLIK\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"🏰 {player['kingdom']}\n\n"

            f"⚜️ Lavozim: {player['position']}\n"
            f"⚔️ Kuch: {player['power']}\n"
            f"🛡️ Mudofaa: {player['defense']}\n\n"

            "Taxt, saroy va qirollik boshqaruvi "
            "guruh o‘yinining asosiy markazi bo‘ladi."
        )

    if key == "profile":

        return lobby_text(player)

    if key == "games":

        return (
            "🎮 O‘YINLAR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "🏰 Guruhdagi THRONE\n"
            "Admin: /startgame\n\n"

            "⚔️ Duel\n"
            "/duel USER_ID\n\n"

            "🏆 Turnir\n"
            "/tournament"
        )

    if key == "inventory":

        return (
            "🎒 INVENTAR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"⚔️ Qurol: {player['weapon']}\n"
            f"🛡️ Zirh: {player['armor']}\n"
            f"🐎 Ot: "
            f"{'Bor' if player['horse'] else 'Yo‘q'}\n"
            f"🧑 Avatar: {player['avatar']}"
        )

    if key == "market":

        return (
            "💰 BOZOR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            "⚔️ Temir qilich — 500 🟡\n"
            "🛡️ Qirollik qalqoni — 700 🟡\n"
            "🐎 Urush oti — 1200 🟡\n"
            "⚜️ Elite Pass — 100 💎"
        )

    if key == "clans":

        connection = db()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                clans.name,
                players.name AS owner
            FROM clans
            LEFT JOIN players
            ON players.user_id = clans.owner_id
            ORDER BY clans.id DESC
            LIMIT 10
        """)

        clans = cursor.fetchall()

        connection.close()

        if not clans:

            body = "Hali klan mavjud emas."

        else:

            body = "\n".join(
                f"🏴 {c['name']} — {c['owner']}"
                for c in clans
            )

        return (
            "🏴 KLANLAR\n"
            "━━━━━━━━━━━━━━━━━━\n\n"

            f"{body}\n\n"

            "Klan yaratish:\n"
            "/createclan KLAN_NOMI"
        )

    if key == "family":

        if player["spouse_id"]:

            spouse = get_player(
     
