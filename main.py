import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# =========================
# THRONE CONFIG
# =========================

CREATOR_ID = 0  # Keyin o'zingning Telegram ID'ingni yozamiz

players = {}


def get_player(user):
    user_id = user.id

    if user_id not in players:
        players[user_id] = {
            "name": user.first_name or "Player",
            "gold": 1000,
            "coin": 100,
            "diamond": 10,
            "elite": False,
            "level": 1,
        }

    player = players[user_id]

    # Creator uchun cheksiz resurslar
    if user_id == CREATOR_ID:
        player["gold"] = float("inf")
        player["coin"] = float("inf")
        player["diamond"] = float("inf")
        player["elite"] = True

    return player


# =========================
# MAIN MENU
# =========================

def main_menu():
    keyboard = [
        [
            InlineKeyboardButton("🎮 O‘yinlar", callback_data="games"),
            InlineKeyboardButton("👤 Profil", callback_data="profile"),
        ],
        [
            InlineKeyboardButton("🏴 Klanlar", callback_data="clans"),
            InlineKeyboardButton("❤️ Oila", callback_data="family"),
        ],
        [
            InlineKeyboardButton("💰 Bozor", callback_data="market"),
            InlineKeyboardButton("📊 Reyting", callback_data="rating"),
        ],
        [
            InlineKeyboardButton("🎁 Mukofotlar", callback_data="rewards"),
            InlineKeyboardButton("📖 Qoidalar", callback_data="rules"),
        ],
        [
            InlineKeyboardButton("⚙️ Sozlamalar", callback_data="settings"),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user)

    if user.id == CREATOR_ID:
        text = (
            "👑 THRONE\n\n"
            "𓆩 ELITE 𓆪 YARATUVCHI\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞\n\n"
            "Qirollik sening qo‘lingda."
        )
    else:
        text = (
            "👑 THRONE\n\n"
            "Qirollik seni kutmoqda.\n\n"
            f"👤 {player['name']}\n"
            f"⭐ Level: {player['level']}\n"
            f"🟡 Oltin: {player['gold']}\n"
            f"🪙 Coin: {player['coin']}\n"
            f"💎 Olmos: {player['diamond']}\n\n"
            "⚔️ Taxt uchun kurash boshlanadi."
        )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# PROFILE
# =========================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    player = get_player(user)

    gold = "∞" if user.id == CREATOR_ID else player["gold"]
    coin = "∞" if user.id == CREATOR_ID else player["coin"]
    diamond = "∞" if user.id == CREATOR_ID else player["diamond"]
    elite = "AKTIV ∞" if user.id == CREATOR_ID else (
        "AKTIV" if player["elite"] else "FAOL EMAS"
    )

    text = (
        "👤 PROFIL\n\n"
        f"Ism: {player['name']}\n"
        f"⭐ Level: {player['level']}\n\n"
        f"🟡 Oltin: {gold}\n"
        f"🪙 Coin: {coin}\n"
        f"💎 Olmos: {diamond}\n"
        f"⚜️ Elite Pass: {elite}"
    )

    keyboard = [
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="home")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# GAMES
# =========================

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⚔️ Qirollik o‘yini", callback_data="kingdom")],
        [InlineKeyboardButton("⚔️ Duel", callback_data="duel")],
        [InlineKeyboardButton("🏆 Turnirlar", callback_data="tournaments")],
        [InlineKeyboardButton("⬅️ Orqaga", callback_data="home")],
    ]

    await query.edit_message_text(
        "🎮 O‘YINLAR\n\n"
        "Qirollikdagi o‘yin rejimini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =========================
# KINGDOM
# =========================

async def kingdom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "👑 QIROLLIK O‘YINI\n\n"
        "⚔️ Qirollik uchun jangga tayyorlaning.\n\n"
        "O‘yin guruhda administrator tomonidan boshlanadi.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="games")]
        ])
    )


# =========================
# DUEL
# =========================

async def duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "⚔️ DUEL\n\n"
        "Raqibingizni tanlang va kuchingizni sinang.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="games")]
        ])
    )


# =========================
# TOURNAMENTS
# =========================

async def tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🏆 TURNIRLAR\n\n"
        "Hozircha faol turnir mavjud emas.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data="games")]
        ])
    )


# =========================
# OTHER SECTIONS
# =========================

async def simple_page(update, title, text, back="home"):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"{title}\n\n{text}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("⬅️ Orqaga", callback_data=back)]
        ])
    )


async def clans(update, context):
    await simple_page(
        update,
        "🏴 KLANLAR",
        "Qirollikdagi klanlaringiz shu yerda boshqariladi."
    )


async def family(update, context):
    await simple_page(
        update,
        "❤️ OILA",
        "Qirollikdagi oilaviy tizim."
    )


async def market(update, context):
    await simple_page(
        update,
        "💰 BOZOR",
        "Oltin, coin, olmos va boshqa buyumlar bozori."
    )


async def rating(update, context):
    await simple_page(
        update,
        "📊 REYTING",
        "Eng kuchli qirolliklar va o‘yinchilar reytingi."
    )


async def rewards(update, context):
    await simple_page(
        update,
        "🎁 MUKOFOTLAR",
        "Kunlik va maxsus mukofotlar shu yerda."
    )


async def rules(update, context):
    await simple_page(
        update,
        "📖 QOIDALAR",
        "THRONE qoidalari keyingi bosqichda to‘liq qo‘shiladi."
    )


async def settings(update, context):
    await simple_page(
        update,
        "⚙️ SOZLAMALAR",
        "Profil va o‘yin sozlamalari."
    )


async def home(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    player = get_player(user)

    await query.edit_message_text(
        f"👑 THRONE\n\n"
        f"Qirollik seni kutmoqda.\n\n"
        f"👤 {player['name']}",
        reply_markup=main_menu()
    )


# =========================
# CALLBACKS
# =========================

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    handlers = {
        "home": home,
        "profile": profile,
        "games": games,
        "kingdom": kingdom,
        "duel": duel,
        "tournaments": tournaments,
        "clans": clans,
        "family": family,
        "market": market,
        "rating": rating,
        "rewards": rewards,
        "rules": rules,
        "settings": settings,
    }

    handler = handlers.get(data)

    if handler:
        await handler(update, context)
    else:
        await query.answer("Bu funksiya hali tayyorlanmoqda.")


# =========================
# RUN
# =========================

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN topilmadi")

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    print("THRONE ishga tushdi...")
    application.run_polling()


if __name__ == "__main__":
    main()
