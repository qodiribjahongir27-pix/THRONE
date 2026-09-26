import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, CREATOR_ID
from database import init_db, get_user, create_user
from keyboards import main_menu

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.economy import router as economy_router
from handlers.kingdom import router as kingdom_router
from handlers.clan import router as clan_router
from handlers.family import router as family_router
from handlers.game import router as game_router


dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: Message):
    user_id = message.from_user.id

    user = await get_user(user_id)

    if not user:
        await create_user(
            user_id=user_id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or "O‘yinchi",
            gold=0,
            coin=0,
            diamond=0,
            elite=0,
        )

    if user_id == CREATOR_ID:
        text = (
            "👑 <b>THRONE</b>\n\n"
            "𓆩 <b>ELITE YARATUVCHI</b> 𓆪\n\n"
            "🟡 Oltin: ∞\n"
            "🪙 Coin: ∞\n"
            "💎 Olmos: ∞\n"
            "⚜️ Elite Pass: AKTIV ∞\n\n"
            "🏰 <b>Sening hukmronliging shu yerdan boshlanadi.</b>"
        )
    else:
        text = (
            f"👑 <b>THRONE'ga xush kelibsiz, "
            f"{message.from_user.full_name}!</b>\n\n"
            "🏰 Bu oddiy o‘yin emas — bu toj, kuch va strategiya olami.\n\n"
            "⚔️ Kuchingizni oshiring.\n"
            "🏴 Klaningizni yarating.\n"
            "💎 Noyob imkoniyatlarni qo‘lga kiriting.\n"
            "👑 Taxt uchun kurashing.\n\n"
            "✨ <b>THRONE — har bir qaror tarixga aylanadi.</b>"
        )

    await message.answer(
        text,
        reply_markup=main_menu()
    )


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)

    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(economy_router)
    dp.include_router(kingdom_router)
    dp.include_router(clan_router)
    dp.include_router(family_router)
    dp.include_router(game_router)

    print("THRONE bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
