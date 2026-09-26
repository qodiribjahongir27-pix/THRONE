from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from config import CREATOR_ID
from database import (
    get_active_game,
    create_game,
    add_game_player,
    get_game_players,
    set_game_status,
    get_user,
    create_user,
)

router = Router()


# =========================
# GAME KEYBOARD
# =========================

def game_lobby_keyboard(is_admin: bool = False):
    buttons = [
        [
            InlineKeyboardButton(
                text="👑 QO‘SHILISH",
                callback_data="game_join"
            ),
            InlineKeyboardButton(
                text="❌ CHIQISH",
                callback_data="game_leave"
            ),
        ],
        [
            InlineKeyboardButton(
                text="👥 O‘YINCHILAR",
                callback_data="game_players"
            ),
            InlineKeyboardButton(
                text="📖 QOIDALAR",
                callback_data="game_rules"
            ),
        ],
    ]

    if is_admin:
        buttons.append([
            InlineKeyboardButton(
                text="▶️ O‘YINNI BOSHLASH",
                callback_data="game_start"
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================
# HELPERS
# =========================

async def ensure_user(message: Message):
    user = await get_user(message.from_user.id)

    if user is None:
        await create_user(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or "O‘yinchi",
        )

    return await get_user(message.from_user.id)


async def get_player_count(game_id: int):
    players = await get_game_players(game_id)
    return len(players)


# =========================
# /newgame
# =========================

@router.message(Command("newgame"))
async def new_game(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        await message.answer(
            "⚔️ THRONE o‘yini faqat guruhda boshlanadi."
        )
        return

    await ensure_user(message)

    active_game = await get_active_game(message.chat.id)

    if active_game:
        await message.answer(
            "⚠️ Bu guruhda allaqachon faol THRONE o‘yini mavjud."
        )
        return

    game_id = await create_game(
        chat_id=message.chat.id,
        host_id=message.from_user.id,
        min_players=7,
        max_players=35,
    )

    await add_game_player(
        game_id=game_id,
        user_id=message.from_user.id,
    )

    text = (
        "👑 <b>THRONE — YANGI O‘YIN</b>\n\n"
        "🏰 Qirollik darvozalari ochildi.\n"
        "Taxt uchun yangi jang boshlanish arafasida.\n\n"
        "👥 O‘yinchilar: <b>1 / 35</b>\n"
        "⚔️ Minimal: <b>7</b>\n\n"
        "👇 O‘yinga qo‘shiling:"
    )

    await message.answer(
        text,
        reply_markup=game_lobby_keyboard(
            is_admin=message.from_user.id == CREATOR_ID
            or message.from_user.id == (await get_user(message.from_user.id))["user_id"]
        ),
    )


# =========================
# /join
# =========================

@router.message(Command("join"))
async def join_game(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    await ensure_user(message)

    game = await get_active_game(message.chat.id)

    if not game:
        await message.answer(
            "⚠️ Hozir faol o‘yin yo‘q.\n"
            "Yangi o‘yin uchun /newgame"
        )
        return

    if game["status"] != "lobby":
        await message.answer(
            "⚠️ O‘yin allaqachon boshlangan."
        )
        return

    players = await get_game_players(game["id"])

    if any(player["user_id"] == message.from_user.id for player in players):
        await message.answer(
            "👑 Siz allaqachon o‘yindasiz."
        )
        return

    if len(players) >= game["max_players"]:
        await message.answer(
            "❌ O‘yinchilar soni maksimal chegaraga yetdi."
        )
        return

    await add_game_player(
        game_id=game["id"],
        user_id=message.from_user.id,
    )

    players = await get_game_players(game["id"])

    await message.answer(
        f"👑 <b>{message.from_user.full_name}</b> o‘yinga qo‘shildi.\n\n"
        f"👥 O‘yinchilar: <b>{len(players)} / {game['max_players']}</b>"
    )


# =========================
# BUTTON JOIN
# =========================

@router.callback_query(F.data == "game_join")
async def game_join_callback(callback: CallbackQuery):
    message = callback.message

    if message.chat.type not in ("group", "supergroup"):
        await callback.answer(
            "O‘yin guruhda ishlaydi.",
            show_alert=True,
        )
        return

    await ensure_user(message)

    game = await get_active_game(message.chat.id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game["status"] != "lobby":
        await callback.answer(
            "O‘yin allaqachon boshlangan.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if any(player["user_id"] == callback.from_user.id for player in players):
        await callback.answer(
            "Siz allaqachon o‘yindasiz.",
            show_alert=True,
        )
        return

    if len(players) >= game["max_players"]:
        await callback.answer(
            "O‘yin to‘ldi.",
            show_alert=True,
        )
        return

    await add_game_player(
        game_id=game["id"],
        user_id=callback.from_user.id,
    )

    await callback.answer(
        "👑 Siz o‘yinga qo‘shildingiz!"
    )

    players = await get_game_players(game["id"])

    await message.answer(
        f"👑 <b>{callback.from_user.full_name}</b> o‘yinga qo‘shildi.\n\n"
        f"👥 O‘yinchilar: <b>{len(players)} / {game['max_players']}</b>"
    )


# =========================
# LEAVE
# =========================

@router.callback_query(F.data == "game_leave")
async def game_leave_callback(callback: CallbackQuery):
    await callback.answer(
        "❌ Chiqish funksiyasi keyingi game-player modulida to‘liq ulanadi.",
        show_alert=True,
    )


# =========================
# PLAYERS
# =========================

@router.callback_query(F.data == "game_players")
async def game_players_callback(callback: CallbackQuery):
    game = await get_active_game(callback.message.chat.id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if not players:
        text = "👥 <b>O‘YINCHILAR</b>\n\nHozircha hech kim yo‘q."
    else:
        lines = []

        for index, player in enumerate(players, start=1):
            user = await get_user(player["user_id"])

            if user:
                name = user["full_name"]
            else:
                name = f"Player {player['user_id']}"

            lines.append(f"{index}. 👤 {name}")

        text = (
            "👥 <b>THRONE O‘YINCHILARI</b>\n\n"
            + "\n".join(lines)
            + f"\n\n👥 Jami: <b>{len(players)}</b>"
        )

    await callback.message.answer(text)
    await callback.answer()


# =========================
# RULES
# =========================

@router.callback_query(F.data == "game_rules")
async def game_rules_callback(callback: CallbackQuery):
    text = (
        "📖 <b>THRONE — O‘YIN QOIDALARI</b>\n\n"
        "👥 Minimal o‘yinchi: <b>7</b>\n"
        "👥 Maksimal o‘yinchi: <b>35</b>\n\n"
        "🌙 Tun — maxfiy harakatlar.\n"
        "☀️ Kun — muhokama va qarorlar.\n"
        "⚖️ Ovoz berish — chiqariladigan o‘yinchini aniqlaydi.\n"
        "🗣️ So‘nggi so‘z — chiqarilgan o‘yinchiga beriladi.\n\n"
        "👑 Yakuniy maqsad — o‘z tomonining g‘alabasiga erishish."
    )

    await callback.message.answer(text)
    await callback.answer()


# =========================
# START GAME
# =========================

@router.callback_query(F.data == "game_start")
async def start_game_callback(callback: CallbackQuery):
    game = await get_active_game(callback.message.chat.id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if callback.from_user.id != game["host_id"] and callback.from_user.id != CREATOR_ID:
        await callback.answer(
            "⛔ O‘yinni faqat o‘yin yaratuvchisi yoki THRONE Creator boshlashi mumkin.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if len(players) < game["min_players"]:
        await callback.answer(
            f"⚠️ O‘yinni boshlash uchun kamida {game['min_players']} o‘yinchi kerak.",
            show_alert=True,
        )
        return

    await set_game_status(
        game["id"],
        "running",
    )

    await callback.message.answer(
        "⚔️ <b>THRONE O‘YINI BOSHLANDI</b>\n\n"
        "🏰 Qirollik eshiklari yopildi.\n"
        "👑 Endi har bir qaror muhim.\n\n"
        "🌙 <b>Birinchi tun boshlanmoqda...</b>"
    )

    await callback.answer()


# =========================
# /start GAME COMMAND
# =========================

@router.message(Command("start"))
async def start_game_command(message: Message):
    """
    /start global bot komandasi bilan to‘qnashmasligi uchun
    hozircha o‘yin boshlamaydi.
    """
    return


# =========================
# /stop
# =========================

@router.message(Command("stop"))
async def stop_game(message: Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    game = await get_active_game(message.chat.id)

    if not game:
        await message.answer(
            "⚠️ Faol o‘yin yo‘q."
        )
        return

    if (
        message.from_user.id != game["host_id"]
        and message.from_user.id != CREATOR_ID
    ):
        await message.answer(
            "⛔ O‘yinni faqat yaratuvchi yoki THRONE Creator to‘xtata oladi."
        )
        return

    await set_game_status(
        game["id"],
        "stopped",
    )

    await message.answer(
        "🛑 <b>THRONE O‘YINI TO‘XTATILDI</b>\n\n"
        "🏰 Ushbu qirollik jangi yakunlandi."
      )
