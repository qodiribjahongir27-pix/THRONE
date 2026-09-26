import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from config import BOT_TOKEN, CREATOR_ID
from database import init_db, get_user, create_user
from keyboards import (
    main_menu,
    language_menu,
    roles_menu,
    role_list_menu,
    role_detail_menu
)
from roles import ROLES


dp = Dispatcher()


# =========================
# /START
# =========================

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


# =========================
# CALLBACKLAR
# =========================

@dp.callback_query()
async def menu_callback(callback: CallbackQuery):

    await callback.answer()

    # =========================
    # 🌐 TIL
    # =========================

    if callback.data == "language":
        await callback.message.edit_text(
            "🌐 <b>Tilni tanlang</b>\n\n"
            "THRONE interfeysi uchun tilni tanlang:",
            reply_markup=language_menu()
        )
        return


    # =========================
    # 🔙 ASOSIY MENYU
    # =========================

    if callback.data == "back_main":
        await callback.message.edit_text(
            "👑 <b>THRONE</b>\n\n"
            "Asosiy menyu:",
            reply_markup=main_menu()
        )
        return


    # =========================
    # 🎭 ROLLAR
    # =========================

    if callback.data == "roles":
        await callback.message.edit_text(
            "🎭 <b>THRONE ROLLARI</b>\n\n"
            "O‘zingiz ko‘rmoqchi bo‘lgan tomonini tanlang:",
            reply_markup=roles_menu()
        )
        return


    # =========================
    # 👑 TAHT TOMONI
    # =========================

    if callback.data == "role_side_throne":

        side = [
            (key, role)
            for key, role in ROLES.items()
            if role["side"] == "Taxt"
        ]

        await callback.message.edit_text(
            "👑 <b>TAHT TOMONI</b>\n\n"
            "Qirollik tarafidagi rollar:",
            reply_markup=role_list_menu(side)
        )
        return


    # =========================
    # 🩸 QORA TOMON
    # =========================

    if callback.data == "role_side_dark":

        side = [
            (key, role)
            for key, role in ROLES.items()
            if role["side"] == "Qora"
        ]

        await callback.message.edit_text(
            "🩸 <b>QORA TOMON</b>\n\n"
            "Qirollikka qarshi yashirin kuchlar:",
            reply_markup=role_list_menu(side)
        )
        return


    # =========================
    # ⚔️ ISYON TOMONI
    # =========================

    if callback.data == "role_side_rebel":

        side = [
            (key, role)
            for key, role in ROLES.items()
            if role["side"] == "Isyon"
        ]

        await callback.message.edit_text(
            "⚔️ <b>ISYON TOMONI</b>\n\n"
            "Qirollikka qarshi isyonchilar:",
            reply_markup=role_list_menu(side)
        )
        return


    # =========================
    # ☠️ MUSTAQIL
    # =========================

    if callback.data == "role_side_independent":

        side = [
            (key, role)
            for key, role in ROLES.items()
            if role["side"] == "Mustaqil"
        ]

        await callback.message.edit_text(
            "☠️ <b>MUSTAQIL ROLLAR</b>\n\n"
            "Hech bir tomonga to‘liq bo‘ysunmaydigan rollar:",
            reply_markup=role_list_menu(side)
        )
        return


    # =========================
    # 🎭 ROL MA'LUMOTI
    # =========================

    if callback.data.startswith("role_"):

        role_key = callback.data.replace("role_", "", 1)

        role = ROLES.get(role_key)

        if not role:
            return

        text = (
            f"{role['name']}\n\n"
            f"🏷 <b>Tomon:</b> {role['side']}\n\n"
            f"📖 <b>Tavsif:</b>\n"
            f"{role['description']}\n\n"
            f"⚔️ <b>Qobiliyat:</b>\n"
            f"{role['ability']}\n\n"
            f"⚠️ <b>Cheklov:</b>\n"
            f"{role['limitation']}\n\n"
            f"🏆 <b>G‘alaba:</b>\n"
            f"{role['win']}"
        )

        await callback.message.edit_text(
            text,
            reply_markup=role_detail_menu()
        )
        return


    # =========================
    # BOSHQA MENYULAR
    # =========================

    messages = {

        "cabinet":
            "👤 <b>KABINET</b>\n\n"
            "Shaxsiy profilingiz.",

        "kingdom":
            "🏰 <b>QIROLLIGIM</b>\n\n"
            "Qirolligingizni boshqaring.",

        "inventory":
            "🎒 <b>INVENTAR</b>\n\n"
            "Barcha buyumlaringiz.",

        "shop":
            "💰 <b>DO‘KON</b>\n\n"
            "Kerakli narsalarni xarid qiling.",

        "clan":
            "🏴 <b>KLANIM</b>\n\n"
            "Klaningizni boshqaring.",

        "family":
            "❤️ <b>OILA</b>\n\n"
            "Oilaviy tizim.",

        "army":
            "⚔️ <b>KUCHLARIM</b>\n\n"
            "Harbiy kuchlaringiz.",

        "tournaments":
            "🏆 <b>MUSOBAQALAR</b>\n\n"
            "Turnirlar.",

        "ranking":
            "📊 <b>REYTING</b>\n\n"
            "O‘yinchilar reytingi.",

        "rewards":
            "🎁 <b>BONUSLAR</b>\n\n"
            "Kunlik va maxsus mukofotlar.",

        "black_market":
            "🕶️ <b>QORA BOZOR</b>\n\n"
            "Noyob takliflar.",

        "elite":
            "⚜️ <b>THRONE ELITE</b>\n\n"
            "Premium imkoniyatlar.",

        "ai":
            "🤖 <b>THRONE AI</b>\n\n"
            "AI yordamchi.",

        "help":
            "❓ <b>YORDAM</b>\n\n"
            "THRONE yordam markazi.",

        "settings":
            "⚙️ <b>SOZLAMALAR</b>\n\n"
            "Bot sozlamalari."
    }


    text = messages.get(
        callback.data,
        "👑 <b>THRONE</b>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=main_menu()
    )


# =========================
# BOTNI ISHGA TUSHIRISH
# =========================

async def main():

    await init_db()

    bot = Bot(token=BOT_TOKEN)

    print("THRONE bot ishga tushdi...")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
