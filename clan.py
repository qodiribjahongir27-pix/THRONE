from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import (
    get_user,
    create_user,
    get_clan,
    create_clan,
    get_clan_members,
    add_clan_member,
    security_log,
)
from keyboards import back_button, clan_menu

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


async def ensure_clan(user_id: int):
    clan = await get_clan(user_id)
    return clan


def clan_text(clan, members=None):
    if clan is None:
        return (
            "🏴 <b>KLANNINGIZ</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "Siz hozircha hech qaysi klanga a'zo emassiz.\n\n"
            "⚔️ Klan — kuchli ittifoq, umumiy maqsad va "
            "birgalikdagi urushlar uchun yaratiladi."
        )

    name = clan["name"] or "Nomsiz klan"
    flag = clan["flag"] or "🏴"
    description = clan["description"] or "Tavsif kiritilmagan."
    level = clan["level"] or 1
    experience = clan["experience"] or 0
    power = clan["power"] or 0
    treasury = clan["treasury"] or 0
    member_count = len(members) if members else 0

    return (
        "🏴 <b>KLANNINGIZ</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"{flag} <b>{name}</b>\n"
        f"📝 {description}\n\n"
        f"⭐ <b>Klan darajasi:</b> {level}\n"
        f"✨ <b>Tajriba:</b> {experience:,} XP\n"
        f"⚔️ <b>Kuch:</b> {power:,}\n"
        f"💰 <b>Klan xazinasi:</b> {treasury:,}\n"
        f"👥 <b>A'zolar:</b> {member_count}\n\n"
        "👑 <i>Kuchli klan — kuchli qirollik.</i>"
    )


@router.callback_query(F.data == "clan")
async def clan_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    clan = await ensure_clan(user_id)

    members = []
    if clan is not None:
        members = await get_clan_members(clan["id"])

    await callback.message.edit_text(
        clan_text(clan, members),
        reply_markup=clan_menu(),
    )

    await callback.answer()


@router.message(Command("clan"))
async def clan_command(message: Message):
    user_id = message.from_user.id

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    clan = await ensure_clan(user_id)

    members = []
    if clan is not None:
        members = await get_clan_members(clan["id"])

    await message.answer(
        clan_text(clan, members),
        reply_markup=clan_menu(),
    )


@router.callback_query(F.data == "create_clan")
async def create_clan_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏴 <b>KLAN YARATISH</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Klan yaratish uchun quyidagi formatdan foydalaning:\n\n"
        "<code>/createclan Klan_nomi</code>\n\n"
        "Masalan:\n"
        "<code>/createclan BLACK CROWN</code>\n\n"
        "⚔️ Klan nomi qirollikdagi boshqa klanlardan "
        "farq qilishi kerak."
    )

    await callback.answer()


@router.message(Command("createclan"))
async def create_clan_command(message: Message):
    user_id = message.from_user.id
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "❌ Klan nomini yozing.\n\n"
            "Masalan:\n"
            "<code>/createclan BLACK CROWN</code>"
        )
        return

    clan_name = parts[1].strip()

    if len(clan_name) < 3:
        await message.answer(
            "❌ Klan nomi kamida 3 ta belgidan iborat bo‘lishi kerak."
        )
        return

    if len(clan_name) > 32:
        await message.answer(
            "❌ Klan nomi 32 belgidan oshmasligi kerak."
        )
        return

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    existing_clan = await get_clan(user_id)

    if existing_clan is not None:
        await message.answer(
            "❌ Siz allaqachon klanga a'zosisiz.\n\n"
            f"🏴 Klan: <b>{existing_clan['name']}</b>"
        )
        return

    try:
        clan_id = await create_clan(
            owner_id=user_id,
            name=clan_name,
            flag="🏴",
            description="Yangi THRONE klani",
        )

        await add_clan_member(
            clan_id=clan_id,
            user_id=user_id,
            role="leader",
        )

        await security_log(
            user_id,
            "create_clan",
            f"clan_id={clan_id}; name={clan_name}",
        )

        await message.answer(
            "👑 <b>KLAN YARATILDI</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"🏴 <b>Nomi:</b> {clan_name}\n"
            "👑 <b>Lavozim:</b> Rahbar\n"
            "⭐ <b>Daraja:</b> 1\n"
            "⚔️ <b>Kuch:</b> 0\n\n"
            "✨ Klaningiz THRONE tarixidagi yangi sahifani boshladi!"
        )

    except Exception:
        await message.answer(
            "❌ Klan yaratishda xatolik yuz berdi.\n"
            "Klan nomi band bo‘lishi yoki tizimda muammo bo‘lishi mumkin."
        )


@router.callback_query(F.data == "clan_members")
async def clan_members_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    clan = await ensure_clan(user_id)

    if clan is None:
        await callback.answer(
            "Siz hali klanga a'zo emassiz.",
            show_alert=True,
        )
        return

    members = await get_clan_members(clan["id"])

    if not members:
        text = (
            "👥 <b>KLAN A'ZOLARI</b>\n\n"
            "Hozircha a'zolar mavjud emas."
        )
    else:
        lines = [
            "👥 <b>KLAN A'ZOLARI</b>",
            "━━━━━━━━━━━━━━━━━━",
            "",
        ]

        for index, member in enumerate(members[:50], start=1):
            member_name = member["full_name"] or "O‘yinchi"
            role = member["role"] or "member"

            role_name = {
                "leader": "👑 Rahbar",
                "commander": "⚔️ Qo‘mondon",
                "officer": "🛡️ Ofitser",
                "member": "👤 A'zo",
            }.get(role, "👤 A'zo")

            lines.append(
                f"{index}. {member_name} — {role_name}"
            )

        text = "\n".join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=back_button(),
    )

    await callback.answer()


@router.message(Command("clans"))
async def clans_command(message: Message):
    await message.answer(
        "🏴 <b>THRONE KLANLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "Bu bo‘limda qirollikdagi barcha faol klanlar, "
        "ularning kuchi va reytingi ko‘rsatiladi.\n\n"
        "🏆 Klan reytingi keyingi tizim bosqichida ulanadi."
    )


@router.callback_query(F.data == "clan_war")
async def clan_war_callback(callback: CallbackQuery):
    clan = await ensure_clan(callback.from_user.id)

    if clan is None:
        await callback.answer(
            "Klan urushida qatnashish uchun avval klanga a'zo bo‘ling.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        "⚔️ <b>KLAN URUSHI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🏴 Sizning klaningiz:\n"
        f"<b>{clan['name']}</b>\n\n"
        "⚔️ Klan urushi tizimi quyidagicha ishlaydi:\n"
        "• Raqib klan tanlanadi\n"
        "• Urush e'lon qilinadi\n"
        "• Tayyorgarlik bosqichi boshlanadi\n"
        "• Hujum va mudofaa amalga oshiriladi\n"
        "• Natija hisoblanadi\n"
        "• G‘olib klan mukofot va reyting oladi\n\n"
        "🏰 Hududlar uchun urushlar ham shu tizimga ulanadi."
    )

    await callback.answer()


@router.message(Command("clanwar"))
async def clan_war_command(message: Message):
    clan = await ensure_clan(message.from_user.id)

    if clan is None:
        await message.answer(
            "❌ Klan urushida qatnashish uchun avval klanga a'zo bo‘ling."
        )
        return

    await message.answer(
        "⚔️ <b>KLAN URUSHI</b>\n\n"
        f"🏴 Sizning klaningiz: <b>{clan['name']}</b>\n\n"
        "Urush tizimi: tayyorgarlik → hujum → mudofaa → natija → mukofot."
    )


@router.message(Command("clanranking"))
async def clan_ranking_command(message: Message):
    await message.answer(
        "🏆 <b>KLAN REYTINGI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "1. 🏴 — Reyting tizimi ishga tushirilmoqda\n"
        "2. 🏴 — Reyting tizimi ishga tushirilmoqda\n"
        "3. 🏴 — Reyting tizimi ishga tushirilmoqda\n\n"
        "⚔️ Klanlar kuchi, urushlar va g‘alabalar asosida "
        "reyting shakllantiriladi."
    )


@router.callback_query(F.data == "clan_ranking")
async def clan_ranking_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏆 <b>KLAN REYTINGI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "⚔️ Klan kuchi\n"
        "🏆 G‘alabalar\n"
        "🏰 Hududlar\n"
        "⭐ Klan darajasi\n"
        "✨ Tajriba\n\n"
        "Reyting tizimi keyingi bosqichlarda "
        "real ma'lumotlar bilan to‘ldiriladi.",
        reply_markup=back_button(),
    )

    await callback.answer()


@router.callback_query(F.data == "leave_clan")
async def leave_clan_callback(callback: CallbackQuery):
    await callback.answer(
        "Klandan chiqish tizimi xavfsiz tasdiqlash oynasi bilan ulanadi.",
        show_alert=True,
    )


@router.message(Command("leaveclan"))
async def leave_clan_command(message: Message):
    await message.answer(
        "⚠️ Klandan chiqish uchun tasdiqlash tizimi keyingi "
        "bosqichda ulanadi."
    )


@router.callback_query(F.data == "back_main")
async def back_main_from_clan(callback: CallbackQuery):
    from keyboards import main_menu

    await callback.message.edit_text(
        "👑 <b>THRONE</b>\n\n"
        "🏰 Qirollik sizni kutmoqda.",
        reply_markup=main_menu(),
    )

    await callback.answer()
