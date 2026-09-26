import asyncio

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, CREATOR_ID
from database import init_db, get_user, create_user
from keyboards import main_menu


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

    await message.answer(
        text,
        reply_markup=main_menu()
    )


@dp.callback_query()
async def menu_callback(callback: CallbackQuery):
    await callback.answer()

    messages = {
        "cabinet": "👤 <b>KABINET</b>\n\nShaxsiy profilingiz shu yerda.",
        "kingdom": "🏰 <b>QIROLLIGIM</b>\n\nQirolligingizni boshqaring.",
        "inventory": "🎒 <b>INVENTAR</b>\n\nBarcha buyumlaringiz shu yerda.",
        "shop": "💰 <b>DO‘KON</b>\n\nKerakli narsalarni xarid qiling.",
        "clan": "🏴 <b>KLANIM</b>\n\nKlaningizni boshqaring.",
        "family": "❤️ <b>OILA</b>\n\nOilaviy tizim shu yerda.",
        "army": "⚔️ <b>KUCHLARIM</b>\n\nQo‘shin va harbiy kuchlaringiz.",
        "tournaments": "🏆 <b>MUSOBAQALAR</b>\n\nTurnirlar tez orada.",
        "roles": "🎭 <b>ROLLAR</b>\n\nTHRONE rollari.",
        "ranking": "📊 <b>REYTING</b>\n\nEng kuchli o‘yinchilar.",
        "rewards": "🎁 <b>BONUSLAR</b>\n\nKunlik va maxsus mukofotlar.",
        "black_market": "🕶️ <b>QORA BOZOR</b>\n\nNoyob takliflar.",
        "elite": "⚜️ <b>THRONE ELITE</b>\n\nPremium imkoniyatlar.",
        "language": "🌐 <b>TIL</b>\n\nTilni tanlang.",
        "ai": "🤖 <b>THRONE AI</b>\n\nYordamchi tez orada ishga tushadi.",
        "help": "❓ <b>YORDAM</b>\n\nTHRONE yordam markazi.",
        "settings": "⚙️ <b>SOZLAMALAR</b>\n\nBot sozlamalari."
    }

    text = messages.get(
        callback.data,
        "👑 THRONE"
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )


async def main():
    await init_db()

    bot = Bot(token=BOT_TOKEN)

    print("THRONE bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
