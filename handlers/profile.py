from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import CREATOR_ID
from database import get_user, create_user
from keyboards import back_button


router = Router()


@router.callback_query(F.data == "cabinet")
async def cabinet_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    user = await get_user(user_id)

    if user is None:
        await create_user(
            user_id=user_id,
            username=callback.from_user.username or "",
            full_name=callback.from_user.full_name or "O‘yinchi",
        )

        user = await get_user(user_id)

    if user is None:
        await callback.answer(
            "Profilni yuklashda xatolik yuz berdi.",
            show_alert=True,
        )
        return

    full_name = user["full_name"] or "O‘yinchi"
    username = user["username"]

    nickname = user["nickname"] or full_name
    flag = user["flag"] or "🏴"

    level = user["level"] or 1
    experience = user["experience"] or 0

    if user_id == CREATOR_ID:
        gold = "∞"
        coin = "∞"
        diamond = "∞"
        elite = "AKTIV ∞"
    else:
        gold = user["gold"] or 0
        coin = user["coin"] or 0
        diamond = user["diamond"] or 0

        elite = "AKTIV" if user["elite"] else "FAOL EMAS"

    username_text = (
        f"@{username}"
        if username
        else "Username yo‘q"
    )

    text = (
        "👤 <b>THRONE KABINETI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"

        f"🏷️ <b>Nik:</b> {nickname}\n"
        f"🏴 <b>Bayroq:</b> {flag}\n"
        f"👤 <b>Username:</b> {username_text}\n\n"

        f"⭐ <b>Daraja:</b> {level}\n"
        f"✨ <b>Tajriba:</b> {experience} XP\n\n"

        "💰 <b>RESURSLAR</b>\n"
        f"🟡 Oltin: <b>{gold}</b>\n"
        f"🪙 Coin: <b>{coin}</b>\n"
        f"💎 Olmos: <b>{diamond}</b>\n\n"

        "⚜️ <b>THRONE ELITE:</b> "
        f"<b>{elite}</b>\n\n"

        "👑 <i>Har bir daraja — yangi imkoniyat.</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_button(),
    )

    await callback.answer()
