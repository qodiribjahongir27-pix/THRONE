from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import CREATOR_ID
from database import (
    get_active_game,
    create_game,
    add_game_player,
    remove_game_player,
    get_game_players,
    set_game_status,
    assign_game_role,
    get_user,
    create_user,
)

from role_engine import assign_roles


router = Router()

MIN_PLAYERS = 7
MAX_PLAYERS = 35


# =========================================================
# USER
# =========================================================

async def ensure_user(user):
    db_user = await get_user(user.id)

    if db_user is None:
        await create_user(
            user_id=user.id,
            username=user.username or "",
            full_name=user.full_name or "O‘yinchi",
        )

    return await get_user(user.id)


# =========================================================
# LOBBY KEYBOARD
# =========================================================

def lobby_keyboard(can_start=False):
    buttons = [
        [
            InlineKeyboardButton(
                text="👑 QO‘SHILISH",
                callback_data="game_join",
            ),
            InlineKeyboardButton(
                text="❌ CHIQISH",
                callback_data="game_leave",
            ),
        ],
        [
            InlineKeyboardButton(
                text="👥 O‘YINCHILAR",
                callback_data="game_players",
            ),
            InlineKeyboardButton(
                text="📖 QOIDALAR",
                callback_data="game_rules",
            ),
        ],
    ]

    if can_start:
        buttons.append([
            InlineKeyboardButton(
                text="▶️ O‘YINNI BOSHLASH",
                callback_data="game_start",
            )
        ])

    return InlineKeyboardMarkup(
        inline_keyboard=buttons
    )


# =========================================================
# /newgame
# =========================================================

@router.message(Command("newgame"))
async def new_game(message: Message):

    if message.chat.type not in ("group", "supergroup"):
        await message.answer(
            "⚔️ THRONE o‘yini faqat guruhda boshlanadi."
        )
        return

    await ensure_user(message.from_user)

    active = await get_active_game(message.chat.id)

    if active:
        await message.answer(
            "⚠️ Bu guruhda allaqachon faol o‘yin mavjud."
        )
        return

    game_id = await create_game(
        chat_id=message.chat.id,
        creator_id=message.from_user.id,
        min_players=MIN_PLAYERS,
        max_players=MAX_PLAYERS,
    )

    await add_game_player(
        game_id=game_id,
        user_id=message.from_user.id,
    )

    await message.answer(
        "👑 <b>THRONE — YANGI O‘YIN</b>\n\n"
        "🏰 Qirollik darvozalari ochildi.\n\n"
        f"👥 O‘yinchilar: <b>1 / {MAX_PLAYERS}</b>\n"
        f"⚔️ Minimal: <b>{MIN_PLAYERS}</b>\n\n"
        "O‘yinga qo‘shiling va taxt uchun kurashing.",
        reply_markup=lobby_keyboard(can_start=True),
    )


# =========================================================
# /join
# =========================================================

@router.message(Command("join"))
async def join_game(message: Message):

    if message.chat.type not in ("group", "supergroup"):
        return

    await ensure_user(message.from_user)

    game = await get_active_game(message.chat.id)

    if not game:
        await message.answer(
            "⚠️ Faol o‘yin yo‘q.\n\n"
            "Yangi o‘yin: /newgame"
        )
        return

    if game["status"] != "lobby":
        await message.answer(
            "⚠️ O‘yin allaqachon boshlangan."
        )
        return

    players = await get_game_players(game["id"])

    if any(
        player["user_id"] == message.from_user.id
        for player in players
    ):
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
        f"👑 <b>{message.from_user.full_name}</b> "
        "o‘yinga qo‘shildi.\n\n"
        f"👥 O‘yinchilar: "
        f"<b>{len(players)} / {game['max_players']}</b>"
    )


# =========================================================
# JOIN BUTTON
# =========================================================

@router.callback_query(F.data == "game_join")
async def join_button(callback: CallbackQuery):

    if not callback.message:
        await callback.answer()
        return

    game = await get_active_game(
        callback.message.chat.id
    )

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game["status"] != "lobby":
        await callback.answer(
            "O‘yin boshlangan.",
            show_alert=True,
        )
        return

    await ensure_user(callback.from_user)

    players = await get_game_players(game["id"])

    if any(
        player["user_id"] == callback.from_user.id
        for player in players
    ):
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
        "👑 O‘yinga qo‘shildingiz!"
    )

    await callback.message.answer(
        f"👤 <b>{callback.from_user.full_name}</b> "
        "o‘yinga qo‘shildi."
    )


# =========================================================
# LEAVE BUTTON
# =========================================================

@router.callback_query(F.data == "game_leave")
async def leave_button(callback: CallbackQuery):

    if not callback.message:
        await callback.answer()
        return

    game = await get_active_game(
        callback.message.chat.id
    )

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game["status"] != "lobby":
        await callback.answer(
            "O‘yin boshlangan.",
            show_alert=True,
        )
        return

    if game["creator_id"] == callback.from_user.id:
        await callback.answer(
            "👑 O‘yin yaratuvchisi chiqolmaydi.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if not any(
        player["user_id"] == callback.from_user.id
        for player in players
    ):
        await callback.answer(
            "Siz o‘yinda emassiz.",
            show_alert=True,
        )
        return

    await remove_game_player(
        game_id=game["id"],
        user_id=callback.from_user.id,
    )

    await callback.answer(
        "❌ O‘yindan chiqdingiz."
    )


# =========================================================
# PLAYERS
# =========================================================

@router.callback_query(F.data == "game_players")
async def players_button(callback: CallbackQuery):

    if not callback.message:
        await callback.answer()
        return

    game = await get_active_game(
        callback.message.chat.id
    )

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if not players:
        text = (
            "👥 <b>THRONE O‘YINCHILARI</b>\n\n"
            "Hozircha o‘yinchi yo‘q."
        )
    else:
        lines = []

        for index, player in enumerate(players, 1):
            name = player["full_name"] or "O‘yinchi"

            lines.append(
                f"{index}. 👤 {name}"
            )

        text = (
            "👥 <b>THRONE O‘YINCHILARI</b>\n\n"
            + "\n".join(lines)
            + f"\n\nJami: <b>{len(players)}</b>"
        )

    await callback.message.answer(text)
    await callback.answer()


# =========================================================
# RULES
# =========================================================

@router.callback_query(F.data == "game_rules")
async def rules_button(callback: CallbackQuery):

    if not callback.message:
        await callback.answer()
        return

    await callback.message.answer(
        "📖 <b>THRONE QOIDALARI</b>\n\n"
        "🌙 Tunda maxfiy harakatlar bajariladi.\n"
        "☀️ Kunduzi muhokama bo‘ladi.\n"
        "⚖️ Ovoz berish orqali o‘yinchi chiqariladi.\n"
        "💬 Chiqarilgan o‘yinchiga so‘nggi so‘z beriladi.\n"
        "👑 Oxirida o‘z tomoningizning g‘alabasiga "
        "erishishingiz kerak.\n\n"
        f"👥 Minimal: <b>{MIN_PLAYERS}</b>\n"
        f"👥 Maksimal: <b>{MAX_PLAYERS}</b>"
    )

    await callback.answer()


# =========================================================
# START GAME
# =========================================================

@router.callback_query(F.data == "game_start")
async def start_game(callback: CallbackQuery):

    if not callback.message:
        await callback.answer()
        return

    game = await get_active_game(
        callback.message.chat.id
    )

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

    # Hozircha faqat o‘yin yaratuvchisi
    # yoki THRONE Creator boshlay oladi.
    if (
        callback.from_user.id != game["creator_id"]
        and callback.from_user.id != CREATOR_ID
    ):
        await callback.answer(
            "⛔ O‘yinni boshlash huquqi sizda yo‘q.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    if len(players) < game["min_players"]:
        await callback.answer(
            f"⚠️ Kamida {game['min_players']} "
            "o‘yinchi kerak.",
            show_alert=True,
        )
        return

    player_data = [
        {
            "user_id": player["user_id"],
            "full_name": player["full_name"],
            "alive": True,
        }
        for player in players
    ]

    # Rollarga ajratish
    assignments = assign_roles(player_data)

    if not assignments:
        await callback.answer(
            "❌ Rollarni taqsimlashda xatolik.",
            show_alert=True,
        )
        return

    for assignment in assignments:

        await assign_game_role(
            game_id=game["id"],
            user_id=assignment["user_id"],
            role_key=assignment["role_key"],
            side=assignment["side"],
        )

        try:
            await callback.bot.send_message(
                assignment["user_id"],
                "👑 <b>THRONE</b>\n\n"
                f"🎭 Sizning rolingiz: "
                f"<b>{assignment['role_key']}</b>\n\n"
                f"🏷 Tomon: <b>{assignment['side']}</b>\n\n"
                "🌙 Birinchi tun boshlandi.",
            )
        except Exception:
            pass

    await set_game_status(
        game["id"],
        "running",
        phase="night",
    )

    await callback.message.answer(
        "⚔️ <b>THRONE — O‘YIN BOSHLANDI</b>\n\n"
        "🎭 Rollar maxfiy tarzda tarqatildi.\n\n"
        "🌙 <b>BIRINCHI TUN</b>\n"
        "Qorong‘ulik tushdi.\n"
        "Endi yashirin qarorlar boshlanadi."
    )

    await callback.answer(
        "👑 O‘yin boshlandi!"
    )


# =========================================================
# /stop
# =========================================================

@router.message(Command("stop"))
async def stop_game(message: Message):

    if message.chat.type not in ("group", "supergroup"):
        return

    game = await get_active_game(
        message.chat.id
    )

    if not game:
        await message.answer(
            "Faol o‘yin yo‘q."
        )
        return

    if (
        message.from_user.id != game["creator_id"]
        and message.from_user.id != CREATOR_ID
    ):
        await message.answer(
            "⛔ Siz o‘yinni to‘xtata olmaysiz."
        )
        return

    await set_game_status(
        game["id"],
        "stopped",
        phase="stopped",
    )

    await message.answer(
        "🛑 <b>THRONE — O‘YIN TO‘XTATILDI</b>\n\n"
        "Qirollikdagi jang vaqtincha yakunlandi."
    )
