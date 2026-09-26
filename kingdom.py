from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import (
    get_user,
    create_user,
    get_kingdom,
    create_kingdom,
    get_castle,
    get_army,
    security_log,
)
from keyboards import back_button, kingdom_menu

router = Router()


async def ensure_user(user_id: int, username: str = "", full_name: str = "O‘yinchi"):
    user = await get_user(user_id)

    if user is None:
        await create_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
        )
        user = await get_user(user_id)

    return user


async def ensure_kingdom(user_id: int):
    kingdom = await get_kingdom(user_id)

    if kingdom is None:
        await create_kingdom(user_id)
        kingdom = await get_kingdom(user_id)

    return kingdom


def kingdom_text(kingdom, castle=None, army=None):
    kingdom_name = kingdom["name"] or "Nomsiz qirollik"
    flag = kingdom["flag"] or "🏴"
    level = kingdom["level"] or 1
    gold = kingdom["gold"] or 0
    population = kingdom["population"] or 0
    defense = kingdom["defense"] or 0
    military = kingdom["military_power"] or 0

    castle_level = 1
    castle_defense = 0

    if castle:
        castle_level = castle["level"] or 1
        castle_defense = castle["defense"] or 0

    soldiers = 0
    archers = 0
    guards = 0
    cavalry = 0

    if army:
        soldiers = army["soldiers"] or 0
        archers = army["archers"] or 0
        guards = army["guards"] or 0
        cavalry = army["cavalry"] or 0

    return (
        "🏰 <b>QIROLLIGIM</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🏷️ <b>Nomi:</b> {kingdom_name}\n"
        f"{flag} <b>Bayroq:</b> {flag}\n\n"
        f"⭐ <b>Qirollik darajasi:</b> {level}\n"
        f"🟡 <b>Qirollik oltini:</b> {gold:,}\n"
        f"👥 <b>Aholi:</b> {population:,}\n"
        f"🛡️ <b>Mudofaa:</b> {defense:,}\n"
        f"⚔️ <b>Harbiy kuch:</b> {military:,}\n\n"
        "🏯 <b>QAL'A</b>\n"
        f"🏰 Daraja: <b>{castle_level}</b>\n"
        f"🛡️ Qal'a mudofaasi: <b>{castle_defense:,}</b>\n\n"
        "⚔️ <b>ARMİYA</b>\n"
        f"🪖 Askarlar: <b>{soldiers:,}</b>\n"
        f"🏹 Kamonchilar: <b>{archers:,}</b>\n"
        f"🛡️ Qo‘riqchilar: <b>{guards:,}</b>\n"
        f"🐎 Suvoriylar: <b>{cavalry:,}</b>\n\n"
        "👑 <i>Har bir qirollik o‘z hukmdorini yaratadi.</i>"
    )


@router.callback_query(F.data == "kingdom")
async def kingdom_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    kingdom = await ensure_kingdom(user_id)

    castle = await get_castle(user_id)
    army = await get_army(user_id)

    if kingdom is None:
        await callback.answer(
            "Qirollikni yuklashda xatolik yuz berdi.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        kingdom_text(kingdom, castle, army),
        reply_markup=kingdom_menu(),
    )

    await callback.answer()


@router.message(Command("kingdom"))
async def kingdom_command(message: Message):
    user_id = message.from_user.id

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    kingdom = await ensure_kingdom(user_id)

    castle = await get_castle(user_id)
    army = await get_army(user_id)

    if kingdom is None:
        await message.answer(
            "❌ Qirollikni yuklashda xatolik yuz berdi."
        )
        return

    await message.answer(
        kingdom_text(kingdom, castle, army),
        reply_markup=kingdom_menu(),
    )


@router.callback_query(F.data == "castle")
async def castle_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    await ensure_kingdom(user_id)

    castle = await get_castle(user_id)

    if castle is None:
        await callback.answer(
            "Qal'a ma'lumotlari topilmadi.",
            show_alert=True,
        )
        return

    level = castle["level"] or 1
    defense = castle["defense"] or 0
    guards = castle["guards"] or 0
    treasury_capacity = castle["treasury_capacity"] or 0

    text = (
        "🏯 <b>QIROLLIK QAL'ASI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🏰 <b>Daraja:</b> {level}\n"
        f"🛡️ <b>Mudofaa:</b> {defense:,}\n"
        f"👮 <b>Qo‘riqchilar:</b> {guards:,}\n"
        f"💰 <b>Xazina sig‘imi:</b> {treasury_capacity:,}\n\n"
        "⚒️ <i>Qal'a rivojlantirilgani sari yangi imkoniyatlar ochiladi.</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_button(),
    )

    await callback.answer()


@router.message(Command("castle"))
async def castle_command(message: Message):
    user_id = message.from_user.id

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    await ensure_kingdom(user_id)

    castle = await get_castle(user_id)

    if castle is None:
        await message.answer("❌ Qal'a ma'lumotlari topilmadi.")
        return

    level = castle["level"] or 1
    defense = castle["defense"] or 0
    guards = castle["guards"] or 0
    treasury_capacity = castle["treasury_capacity"] or 0

    await message.answer(
        "🏯 <b>QIROLLIK QAL'ASI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🏰 Daraja: <b>{level}</b>\n"
        f"🛡️ Mudofaa: <b>{defense:,}</b>\n"
        f"👮 Qo‘riqchilar: <b>{guards:,}</b>\n"
        f"💰 Xazina sig‘imi: <b>{treasury_capacity:,}</b>"
    )


@router.callback_query(F.data == "army")
async def army_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    await ensure_kingdom(user_id)

    army = await get_army(user_id)

    if army is None:
        await callback.answer(
            "Armiya ma'lumotlari topilmadi.",
            show_alert=True,
        )
        return

    soldiers = army["soldiers"] or 0
    archers = army["archers"] or 0
    guards = army["guards"] or 0
    cavalry = army["cavalry"] or 0
    special_units = army["special_units"] or 0

    total = soldiers + archers + guards + cavalry + special_units

    text = (
        "⚔️ <b>QIROLLIK ARMIYASI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🪖 Askarlar: <b>{soldiers:,}</b>\n"
        f"🏹 Kamonchilar: <b>{archers:,}</b>\n"
        f"🛡️ Qo‘riqchilar: <b>{guards:,}</b>\n"
        f"🐎 Suvoriylar: <b>{cavalry:,}</b>\n"
        f"⚔️ Maxsus birliklar: <b>{special_units:,}</b>\n\n"
        f"👥 <b>Jami qo‘shin:</b> {total:,}\n\n"
        "👑 <i>Armiyani kuchaytirish — qirollikni kuchaytirishdir.</i>"
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_button(),
    )

    await callback.answer()


@router.message(Command("army"))
async def army_command(message: Message):
    user_id = message.from_user.id

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    await ensure_kingdom(user_id)

    army = await get_army(user_id)

    if army is None:
        await message.answer("❌ Armiya ma'lumotlari topilmadi.")
        return

    soldiers = army["soldiers"] or 0
    archers = army["archers"] or 0
    guards = army["guards"] or 0
    cavalry = army["cavalry"] or 0
    special_units = army["special_units"] or 0

    total = soldiers + archers + guards + cavalry + special_units

    await message.answer(
        "⚔️ <b>QIROLLIK ARMIYASI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🪖 Askarlar: <b>{soldiers:,}</b>\n"
        f"🏹 Kamonchilar: <b>{archers:,}</b>\n"
        f"🛡️ Qo‘riqchilar: <b>{guards:,}</b>\n"
        f"🐎 Suvoriylar: <b>{cavalry:,}</b>\n"
        f"⚔️ Maxsus birliklar: <b>{special_units:,}</b>\n\n"
        f"👥 Jami qo‘shin: <b>{total:,}</b>"
    )


@router.callback_query(F.data == "throne")
async def throne_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    await ensure_kingdom(user_id)

    text = (
        "👑 <b>THRONE — TAHT</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🏛️ <b>Qirollik boshqaruvi</b>\n\n"
        "👑 Hukmdor: <b>Siz</b>\n"
        "🏰 Saroy: <b>Faol</b>\n"
        "⚔️ Armiya: <b>Boshqaruv ostida</b>\n"
        "💰 Xazina: <b>Faol</b>\n\n"
        "📜 Bu bo‘lim orqali keyinchalik:\n"
        "• qirollik farmonlari\n"
        "• saroy lavozimlari\n"
        "• qirollik qarorlari\n"
        "• boshqaruv imkoniyatlari\n"
        "amalga oshiriladi."
    )

    await callback.message.edit_text(
        text,
        reply_markup=back_button(),
    )

    await callback.answer()


@router.message(Command("throne"))
async def throne_command(message: Message):
    await message.answer(
        "👑 <b>THRONE — TAHT</b>\n\n"
        "🏛️ Qirollik boshqaruvi markazi.\n\n"
        "⚔️ Farmonlar, saroy va hukmdorlik tizimi "
        "keyingi bosqichlarda shu yerda boshqariladi."
    )


@router.callback_query(F.data == "back_main")
async def back_main_handler(callback: CallbackQuery):
    from keyboards import main_menu

    await callback.message.edit_text(
        "👑 <b>THRONE</b>\n\n"
        "🏰 Qirollik sizni kutmoqda.",
        reply_markup=main_menu(),
    )

    await callback.answer()
