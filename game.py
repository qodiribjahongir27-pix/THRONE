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
    eliminate_game_player,
    add_game_action,
    get_game_actions,
    add_game_vote,
    get_game_votes,
    clear_game_votes,
    save_game_result,
    get_user,
    create_user,
)

from game.role_engine import (
    assign_roles,
    get_assignment_details,
)

from game.night import (
    create_night_state,
    add_night_action,
    execute_night_actions,
    build_night_summary,
)

from game.voting import (
    create_voting_state,
    cast_vote,
    calculate_result,
)

from game.victory import (
    check_victory,
    build_victory_message,
)


router = Router()


# =========================================================
# GAME SETTINGS
# =========================================================

MIN_PLAYERS = 7
MAX_PLAYERS = 35


# =========================================================
# TEMPORARY ACTIVE GAME STATES
# =========================================================

NIGHT_STATES = {}
VOTING_STATES = {}


# =========================================================
# USER HELPER
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

def game_lobby_keyboard(is_admin=False):
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

    if is_admin:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="▶️ O‘YINNI BOSHLASH",
                    callback_data="game_start",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================================================
# TARGET KEYBOARD
# =========================================================

def target_keyboard(players, action):
    buttons = []

    for player in players:
        if not player.get("alive", 1):
            continue

        user_id = player["user_id"]

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"👤 {player.get('full_name', user_id)}",
                    callback_data=f"game_act:{action}:{user_id}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# =========================================================
# VOTE KEYBOARD
# =========================================================

def vote_keyboard(players):
    buttons = []

    for player in players:
        if not player.get("alive", 1):
            continue

        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"⚖️ {player.get('full_name', player['user_id'])}",
                    callback_data=f"game_vote:{player['user_id']}",
                )
            ]
        )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


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

    active_game = await get_active_game(message.chat.id)

    if active_game:
        await message.answer(
            "⚠️ Bu guruhda allaqachon faol THRONE o‘yini mavjud."
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

    is_creator = message.from_user.id == CREATOR_ID

    text = (
        "👑 <b>THRONE — YANGI O‘YIN</b>\n\n"
        "🏰 Qirollik darvozalari ochildi.\n"
        "Taxt uchun yangi jang boshlanish arafasida.\n\n"
        f"👥 O‘yinchilar: <b>1 / {MAX_PLAYERS}</b>\n"
        f"⚔️ Minimal: <b>{MIN_PLAYERS}</b>\n\n"
        "👇 O‘yinga qo‘shiling."
    )

    await message.answer(
        text,
        reply_markup=game_lobby_keyboard(
            is_admin=is_creator or True
        ),
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
            "⚠️ Hozir faol o‘yin yo‘q.\n\n"
            "Yangi o‘yin uchun /newgame"
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
async def game_join_callback(callback: CallbackQuery):

    message = callback.message

    if message.chat.type not in ("group", "supergroup"):
        await callback.answer(
            "O‘yin faqat guruhda ishlaydi.",
            show_alert=True,
        )
        return

    await ensure_user(callback.from_user)

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
        "👑 Siz o‘yinga qo‘shildingiz!"
    )

    players = await get_game_players(game["id"])

    await message.answer(
        f"👑 <b>{callback.from_user.full_name}</b> "
        "o‘yinga qo‘shildi.\n\n"
        f"👥 O‘yinchilar: "
        f"<b>{len(players)} / {game['max_players']}</b>"
    )


# =========================================================
# LEAVE
# =========================================================

@router.callback_query(F.data == "game_leave")
async def game_leave_callback(callback: CallbackQuery):

    game = await get_active_game(callback.message.chat.id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game["status"] != "lobby":
        await callback.answer(
            "O‘yin boshlanganidan keyin chiqib bo‘lmaydi.",
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

    if game["creator_id"] == callback.from_user.id:
        await callback.answer(
            "👑 O‘yin yaratuvchisi lobbydan chiqolmaydi.",
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

    await callback.message.answer(
        f"❌ <b>{callback.from_user.full_name}</b> "
        "o‘yindan chiqdi."
    )


# =========================================================
# PLAYERS
# =========================================================

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
        text = (
            "👥 <b>THRONE O‘YINCHILARI</b>\n\n"
            "Hozircha hech kim yo‘q."
        )
    else:
        lines = []

        for index, player in enumerate(players, start=1):

            user = await get_user(player["user_id"])

            if user:
                name = user["full_name"]
            else:
                name = f"Player {player['user_id']}"

            lines.append(
                f"{index}. 👤 {name}"
            )

        text = (
            "👥 <b>THRONE O‘YINCHILARI</b>\n\n"
            + "\n".join(lines)
            + f"\n\n👥 Jami: <b>{len(players)}</b>"
        )

    await callback.message.answer(text)

    await callback.answer()


# =========================================================
# RULES
# =========================================================

@router.callback_query(F.data == "game_rules")
async def game_rules_callback(callback: CallbackQuery):

    text = (
        "📖 <b>THRONE — O‘YIN QOIDALARI</b>\n\n"

        f"👥 Minimal o‘yinchi: <b>{MIN_PLAYERS}</b>\n"
        f"👥 Maksimal o‘yinchi: <b>{MAX_PLAYERS}</b>\n\n"

        "🌙 <b>TUN</b>\n"
        "Maxfiy qobiliyatlar va harakatlar bajariladi.\n\n"

        "☀️ <b>KUN</b>\n"
        "O‘yinchilar muhokama qiladi.\n\n"

        "⚖️ <b>OVOZ BERISH</b>\n"
        "O‘yinchilar gumon qilingan shaxsni tanlaydi.\n\n"

        "🗣️ <b>SO‘NGGI SO‘Z</b>\n"
        "Eliminatsiya qilingan o‘yinchiga so‘nggi so‘z beriladi.\n\n"

        "👑 <b>MAQSAD</b>\n"
        "O‘z tomoningizning g‘alabasiga erishish."
    )

    await callback.message.answer(text)

    await callback.answer()


# =========================================================
# START GAME
# =========================================================

@router.callback_query(F.data == "game_start")
async def start_game_callback(callback: CallbackQuery):

    game = await get_active_game(callback.message.chat.id)

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

    if (
        callback.from_user.id != game["creator_id"]
        and callback.from_user.id != CREATOR_ID
    ):
        await callback.answer(
            "⛔ O‘yinni faqat o‘yin yaratuvchisi "
            "yoki THRONE Creator boshlashi mumkin.",
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

    # -----------------------------------------------------
    # PREPARE PLAYER DATA
    # -----------------------------------------------------

    player_data = []

    for player in players:

        user = await get_user(player["user_id"])

        player_data.append(
            {
                "user_id": player["user_id"],
                "full_name": (
                    user["full_name"]
                    if user
                    else f"Player {player['user_id']}"
                ),
                "alive": True,
            }
        )

    # -----------------------------------------------------
    # ASSIGN ROLES
    # -----------------------------------------------------

    assignments = assign_roles(player_data)

    if not assignments:
        await callback.answer(
            "❌ Rollarni taqsimlashda xatolik.",
            show_alert=True,
        )
        return

    # -----------------------------------------------------
    # SAVE ROLES
    # -----------------------------------------------------

    for assignment in assignments:

        await assign_game_role(
            game_id=game["id"],
            user_id=assignment["user_id"],
            role_key=assignment["role_key"],
            side=assignment["side"],
        )

    await set_game_status(
        game["id"],
        "running",
        phase="night",
    )

    # -----------------------------------------------------
    # CREATE NIGHT
    # -----------------------------------------------------

    NIGHT_STATES[game["id"]] = create_night_state()

    # -----------------------------------------------------
    # PRIVATE ROLE MESSAGES
    # -----------------------------------------------------

    for assignment in assignments:

        user_id = assignment["user_id"]

        details = get_assignment_details(
            assignment
        )

        role_name = details.get(
            "role_name",
            assignment["role_key"],
        )

        side = details.get(
            "side",
            assignment["side"],
        )

        description = details.get(
            "description",
            "",
        )

        ability = details.get(
            "ability",
            "",
        )

        try:
            await callback.bot.send_message(
                user_id,
                (
                    "👑 <b>THRONE — SIZNING ROLINGIZ</b>\n\n"
                    f"🎭 <b>{role_name}</b>\n\n"
                    f"🏷 Tomon: <b>{side}</b>\n\n"
                    f"📖 {description}\n\n"
                    f"⚔️ <b>Qobiliyat:</b>\n{ability}\n\n"
                    "🌙 Birinchi tun boshlandi."
                ),
            )
        except Exception:
            pass

    # -----------------------------------------------------
    # GROUP MESSAGE
    # -----------------------------------------------------

    await callback.message.answer(
        "⚔️ <b>THRONE — O‘YIN BOSHLANDI</b>\n\n"
        "🏰 Qirollik eshiklari yopildi.\n"
        "🎭 Rollar barcha o‘yinchilarga maxfiy yuborildi.\n\n"
        "🌙 <b>BIRINCHI TUN</b>\n\n"
        "Qorong‘ulik tushdi.\n"
        "Endi yashirin qarorlar boshlanadi."
    )

    await callback.answer(
        "👑 O‘yin boshlandi!"
    )


# =========================================================
# NIGHT ACTION BUTTON
# =========================================================

@router.callback_query(F.data.startswith("game_act:"))
async def game_action_callback(callback: CallbackQuery):

    parts = callback.data.split(":")

    if len(parts) != 3:
        await callback.answer(
            "❌ Noto‘g‘ri harakat.",
            show_alert=True,
        )
        return

    action_type = parts[1]
    target_id = int(parts[2])

    game = await get_active_game(callback.message.chat.id)

    if not game:
        await callback.answer(
            "Faol o‘yin yo‘q.",
            show_alert=True,
        )
        return

    if game["phase"] != "night":
        await callback.answer(
            "🌙 Hozir tun emas.",
            show_alert=True,
        )
        return

    players = await get_game_players(game["id"])

    me = None
    target = None

    for player in players:

        if player["user_id"] == callback.from_user.id:
            me = player

        if player["user_id"] == target_id:
            target = player

    if me is None or not me["alive"]:
        await callback.answer(
            "❌ Siz bu harakatni bajara olmaysiz.",
            show_alert=True,
        )
        return

    if target is None or not target["alive"]:
        await callback.answer(
            "❌ Bu o‘yinchi faol emas.",
            show_alert=True,
        )
        return

    role_key = me["role_key"]

    action_map = {
        "observe": "observer",
        "protect": "protector",
        "block": "blocker",
        "poison": "poison",
        "weaken": "weaken",
        "attack": "attacker",
        "special": "special",
    }

    real_action = action_map.get(
        action_type,
        "special",
    )

    state = NIGHT_STATES.setdefault(
        game["id"],
        create_night_state(),
    )

    add_night_action(
        state=state,
        player_id=callback.from_user.id,
        role_key=role_key,
        action_type=real_action,
        target_id=target_id,
    )

    await add_game_action(
        game_id=game["id"],
        user_id=callback.from_user.id,
        role_key=role_key,
        action_type=real_action,
        target_id=target_id,
    )

    await callback.answer(
        "🌙 Harakatingiz qabul qilindi."
    )


# =========================================================
# BEGIN DAY
# =========================================================

async def begin_day(bot, chat_id, game_id):

    state = NIGHT_STATES.get(game_id)

    if state is None:
        return

    results = execute_night_actions(state)

    players = await get_game_players(game_id)

    deaths = results.get(
        "dead_players",
        [],
    )

    eliminated_ids = []

    for user_id in deaths:

        player = next(
            (
                p
                for p in players
                if p["user_id"] == user_id
            ),
            None,
        )

        if player and player["alive"]:

            await eliminate_game_player(
                game_id=game_id,
                user_id=user_id,
            )

            eliminated_ids.append(user_id)

    await set_game_status(
        game_id,
        "running",
        phase="day",
    )

    summary = build_night_summary(results)

    await bot.send_message(
        chat_id,
        summary,
    )

    if eliminated_ids:

        players_after = await get_game_players(
            game_id
        )

        victory = check_victo
