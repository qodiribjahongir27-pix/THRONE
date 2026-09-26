import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, CREATOR_ID
from database import init_db, get_user, create_user


dp = Dispatcher()


@dp.message(CommandStart())
async def start_command(message: Message):
    user = await get_user(message.from_user.id)

    if not user:
        is_creator = message.from_user.id == CREATOR_ID

        await create_user(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name,
            gold=-1 if is_creator else 0,
            coin=-1 if is_creator else 0,
            diamond=-1 if is_creator else 0,
            elite=1 if is_creator else 0
        )

    if message.from_user.id == CREATOR_ID:
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

    await message.answer(text)


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)

    print("THRONE bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
