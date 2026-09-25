import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# ==================================================
# THRONE CONFIG
# ==================================================

# Hozircha 0.
# Keyin o'zingizning Telegram ID'ingizni qo'yamiz.
CREATOR_ID = 0

players = {}
games = {}


# ==================================================
# PLAYER
# ==================================================

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

    # Faqat creator uchun cheksiz resurs
    if user_id == CREATOR_ID:
        player["gold"] = float("inf")
        player["coin"] = float("inf")
        player["diamond"] = float("inf")
        player["elite"] = True

    return player


# ==================================================
# MAIN MENU
# ==================================================

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


# ==================================================
# PRIVATE START
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat

    player = get_player(user)

    # GROUP
    if chat.type in ["group", "supergroup"]:
        await update.message.reply_text(
            "👑 THRONE\n\n"
            "⚔️ Qirollik o‘yini guruhga tayyor.\n\n"
            "👑 O‘yinni boshlash uchun guruh administratori:\n"
            "/startgame\n\n"
            "📖 Qoidalar: /rules\n"
            "👤 Profil: /profile"
        )
        return

    # PRIVATE
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


# ==================================================
# PROFILE
# ==================================================

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user)

    gold = "∞" if user.id == CREATOR_ID else player["gold"]
    coin = "∞" if user.id == CREATOR_ID else player["coin"]
    diamond = "∞" if user.id == CREATOR_ID else player["diamond"]

    if user.id == CREATOR_ID:
        elite = "AKTIV ∞"
    else:
        elite = "AKTIV" if player["elite"] else "FAOL EMAS"

    text = (
        "👤 PROFIL\n\n"
        f"Ism: {player['name']}\n"
        f"⭐ Level: {player['level']}\n\n"
        f"🟡 Oltin: {gold}\n"
        f"🪙 Coin: {coin}\n"
        f"💎 Olmos: {diamond}\n"
        f"⚜️ Elite Pass: {elite}"
    )

    # Callback orqali
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬅️ Orqaga", callback_data="home")]
            ])
        )

    # Command orqali
    elif update.message:
        await update.message.reply_text(text)


# ==================================================
# GROUP PROFILE
# ==================================================

async def group_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    player = get_player(user)

    gold = "∞" if user.id == CREATOR_ID else player["gold"]
    coin = "∞" if user.id == CREATOR_ID else player["coin"]
    diamond = "∞" if user.id == CREATOR_ID else player["diamond"]

    await update.message.reply_text(
        "👤 PROFIL\n\n"
        f"Ism: {player['name']}\n"
        f"⭐ Level: {player['level']}\n"
        f"🟡 Oltin: {gold}\n"
        f"🪙 Coin: {coin}\n"
        f"💎 Olmos: {diamond}"
    )


# ==================================================
# GROUP GAME
# ==================================================

async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "⚠️ Bu buyruq faqat guruhda ishlaydi."
        )
        return

    member = await context.bot.get_chat_member(
        chat.id,
        user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text(
            "🔒 O‘yinni faqat guruh administratori boshlashi mumkin."
        )
        return

    if chat.id in games and games[chat.id]["active"]:
        await update.message.reply_text(
            "⚔️ Bu guruhda o‘yin allaqachon davom etmoqda."
        )
        return

    games[chat.id] = {
        "active": True,
        "players": [],
        "started_by": user.id,
    }

    await update.message.reply_text(
        "👑 THRONE — QIROLLIK O‘YINI\n\n"
        "⚔️ O‘yin boshlandi!\n\n"
        "🏰 Qirollik o‘yinchilarga tayyor.\n"
        "👥 Ishtirok etish uchun:\n"
        "/join\n\n"
        "⏳ Qirollik eshiklari ochildi."
    )


# ==================================================
# JOIN GAME
# ==================================================

async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(
            "⚠️ Bu buyruq faqat guruhda ishlaydi."
        )
        return

    if chat.id not in games or not games[chat.id]["active"]:
        await update.message.reply_text(
            "⚠️ Hozir guruhda faol o‘yin yo‘q.\n\n"
            "Admin /startgame orqali o‘yinni boshlashi mumkin."
        )
        return

    game_players = games[chat.id]["players"]

    if user.id in game_players:
        await update.message.reply_text(
            "✅ Siz allaqachon o‘yindasiz."
        )
        return

    game_players.append(user.id)

    await update.message.reply_text(
        f"⚔️ {user.first_name} qirollikka qo‘shildi!\n\n"
        f"👥 O‘yinchilar soni: {len(game_players)}"
    )


# ==================================================
# STOP GAME
# ==================================================

async def stop_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    if chat.type not in ["group", "supergroup"]:
        return

    member = await context.bot.get_chat_member(
        chat.id,
        user.id
    )

    if member.status not in ["administrator", "creator"]:
        await update.message.reply_text(
            "🔒 O‘yinni faqat administrator to‘xtata oladi."
        )
        return

    if chat.id not in games or not games[chat.id]["active"]:
        await update.message.reply_text(
            "⚠️ Faol o‘yin yo‘q."
        )
        return

    games[chat.id]["active"] = False

    await update.message.reply_text(
        "🛑 THRONE\n\n"
        "Qirollik o‘yini administrator tomonidan to‘xtatildi."
    )


# ==================================================
# RULES
# ==================================================

async def rules_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 THRONE QOIDALARI\n\n"
        "1️⃣ O‘yinni faqat guruh administratori boshlaydi.\n"
        "2️⃣ O‘yinchilar /join orqali qo‘shiladi.\n"
        "3️⃣ O‘yin davomida barcha qarorlar qirollik tizimi orqali amalga oshiriladi.\n"
        "4️⃣ Adolatli o‘yin va guruh qoidalariga rioya qilish talab qilinadi.\n\n"
        "👑 THRONE"
    )


# ==================================================
# GAMES MENU
# ==================================================

async def games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton(
                "⚔️ Qirollik o‘yini",
                callback_data="kingdom"
            )
        ],
        [
            InlineKeyboardButton(
                "⚔️ Duel",
                callback_data="duel"
            )
        ],
        [
            InlineKeyboardButton(
                "🏆 Turnirlar",
                callback_data="tournaments"
            )
        ],
        [
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data="home"
            )
        ],
    ]

    await query.edit_message_text(
        "🎮 O‘YINLAR\n\n"
        "Qirollikdagi o‘yin rejimini tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ==================================================
# KINGDOM
# ==================================================

async def kingdom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "👑 QIROLLIK O‘YINI\n\n"
        "⚔️ Qirollik uchun jangga tayyorlaning.\n\n"
        "O‘yin guruhda administrator tomonidan boshlanadi.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="games"
                )
            ]
        ])
    )


# ==================================================
# DUEL
# ==================================================

async def duel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "⚔️ DUEL\n\n"
        "Raqibingizni tanlang va kuchingizni sinang.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="games"
                )
            ]
        ])
    )


# ==================================================
# TOURNAMENTS
# ==================================================

async def tournaments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        "🏆 TURNIRLAR\n\n"
        "Hozircha faol turnir mavjud emas.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="games"
                )
            ]
        ])
    )


# ==================================================
# SIMPLE PAGES
# ==================================================

async def simple_page(update, title, text):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(
        f"{title}\n\n{text}",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "⬅️ Orqaga",
                    callback_data="home"
                )
            ]
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


async def rules_page(update, context):
    await simple_page(
        update,
        "📖 QOIDALAR",
        "THRONE qoidalari shu yerda."
    )


async def settings(update, context):
    await simple_page(
        update,
        "⚙️ SOZLAMALAR",
        "Profil va o‘yin sozlamalari."
    )


# ==================================================
# HOME
# ==================================================

async def home(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    player = get_player(user)

    await query.edit_message_text(
        "👑 THRONE\n\n"
        "Qirollik seni kutmoqda.\n\n"
        f"👤 {player['name']}\n"
        f"⭐ Level: {player['level']}",
        reply_markup=main_menu()
    )


# ==================================================
# CALLBACK HANDLER
# ==================================================

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
        "rules": rules_page,
        "settings": settings,
    }

    handler = handlers.get(data)

    if handler:
        await handler(update, context)
    else:
        await query.answer(
            "Bu funksiya hali tayyorlanmoqda."
        )


# ==================================================
# MAIN
# ==================================================

def main():
    if not BOT_TOKEN:
        raise RuntimeError(
            "BOT_TOKEN topilmadi. Railway Variables ichida BOT_TOKEN bo‘lishi kerak."
        )

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # Private + group
    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("profile", group_profile)
    )

    application.add_handler(
        CommandHandler("startgame", start_game)
    )

    application.add_handler(
        CommandHandler("join", join_game)
    )

    application.add_handler(
        CommandHandler("stopgame", stop_game)
    )

    application.add_handler(
        CommandHandler("rules", rules_command)
    )

    # Buttons
    application.add_handler(
        CallbackQueryHandler(callback_handler)
    )

    print("👑 THRONE ishga tushdi...")

    application.run_polling()


if __name__ == "__main__":
    main()
