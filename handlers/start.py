from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import CREATOR_ID
from database import (
    get_user,
    create_user,
    update_user_info,
)
from keyboards import main_menu


router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "O‘yinchi"

    user = await get_user(user_id)

    if user is None:
        await create_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
        )
    else:
        await update_user_info(
            user_id=user_id,
            username=username,
            full_name=full_name,
        )

    if user_id == CREATOR_ID:
        text = (
            "👑 <b>THRONE</b>\n"
            "𓆩 <b>ELITE YARATUVCHI</b> 𓆪\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞\n\n"
            "🏰 <b>Sening hukmronliging shu yerdan boshlanadi.</b>"
        )
    else:
        text = (
            f"👑 <b>THRONE'ga xush kelibsiz, {full_name}!</b>\n\n"
            "🏰 Bu oddiy o‘yin emas — bu toj, kuch va strategiya olami.\n\n"
            "⚔️ Kuchingizni oshiring.\n"
            "🏴 Klaningizni yarating.\n"
            "💎 Noyob imkoniyatlarni qo‘lga kiriting.\n"
            "👑 Taxt uchun kurashing.\n\n"
            "✨ <b>THRONE — har bir qaror tarixga aylanadi.</b>"
        )

    await message.answer(
        text,
        reply_markup=main_menu(),
    )
