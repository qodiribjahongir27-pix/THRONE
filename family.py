from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import (
    get_user,
    create_user,
    get_family,
    create_family,
    create_family_proposal,
    get_family_proposal,
    update_family_proposal,
    get_pending_family_proposal,
)
from keyboards import back_button

router = Router()


# ============================================================
# HELPERS
# ============================================================

async def ensure_user(
    user_id: int,
    username: str = "",
    full_name: str = "O‘yinchi",
):
    user = await get_user(user_id)

    if user is None:
        await create_user(
            user_id=user_id,
            username=username,
            full_name=full_name,
        )
        user = await get_user(user_id)

    return user


def proposal_keyboard(proposal_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="❤️ QABUL QILISH",
        callback_data=f"family_accept:{proposal_id}",
    )

    builder.button(
        text="❌ RAD ETISH",
        callback_data=f"family_reject:{proposal_id}",
    )

    builder.adjust(1)

    return builder.as_markup()


def family_text(family, current_user_id: int):
    if family is None:
        return (
            "❤️ <b>THRONE OILASI</b>\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "💍 Siz hozircha nikohda emassiz.\n\n"
            "❤️ Oila — THRONE'dagi ikki o‘yinchi "
            "o‘rtasidagi alohida rishta.\n\n"
            "👑 Nikoh faqat Telegram guruhida taklif "
            "orqali amalga oshiriladi."
        )

    if family["user1_id"] == current_user_id:
        spouse_id = family["user2_id"]
    else:
        spouse_id = family["user1_id"]

    return (
        "❤️ <b>THRONE OILASI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💍 <b>Turmush o‘rtog‘ingiz:</b> "
        f"<code>{spouse_id}</code>\n\n"
        f"⭐ <b>Oila darajasi:</b> {family['family_level']}\n"
        f"✨ <b>Oilaviy tajriba:</b> "
        f"{family['family_experience']:,} XP\n"
        f"💰 <b>Oilaviy oltin:</b> "
        f"{family['family_gold']:,}\n\n"
        f"📅 <b>Nikoh sanasi:</b> "
        f"{family['married_at']}\n\n"
        "🏰 <i>Ikki qalb — bitta xonadon.</i>"
    )


# ============================================================
# FAMILY PANEL
# ============================================================

@router.callback_query(F.data == "family")
async def family_callback(callback: CallbackQuery):
    user_id = callback.from_user.id

    await ensure_user(
        user_id,
        callback.from_user.username or "",
        callback.from_user.full_name or "O‘yinchi",
    )

    family = await get_family(user_id)

    await callback.message.edit_text(
        family_text(family, user_id),
        reply_markup=back_button(),
    )

    await callback.answer()


@router.message(Command("family"))
async def family_command(message: Message):
    user_id = message.from_user.id

    await ensure_user(
        user_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    family = await get_family(user_id)

    await message.answer(
        family_text(family, user_id),
        reply_markup=back_button(),
    )


# ============================================================
# MARRIAGE PROPOSAL
# ============================================================

@router.message(Command("marry"))
async def marry_command(message: Message):
    # Nikoh faqat guruhda boshlanadi.
    if message.chat.type not in {"group", "supergroup"}:
        await message.answer(
            "❌ Nikoh taklifi faqat Telegram guruhida yuboriladi."
        )
        return

    sender_id = message.from_user.id

    await ensure_user(
        sender_id,
        message.from_user.username or "",
        message.from_user.full_name or "O‘yinchi",
    )

    # Eng qulay usul — /marry buyrug‘ini kerakli odamning
    # xabariga Reply qilib yuborish.
    if message.reply_to_message is None:
        await message.answer(
            "💍 <b>Nikoh taklifi</b>\n\n"
            "Taklif yubormoqchi bo‘lgan odamning xabariga "
            "Reply qilib:\n\n"
            "<code>/marry</code>\n\n"
            "deb yuboring."
        )
        return

    target = message.reply_to_message.from_user

    if target is None:
        await message.answer(
            "❌ Foydalanuvchini aniqlab bo‘lmadi."
        )
        return

    receiver_id = target.id

    if receiver_id == sender_id:
        await message.answer(
            "❌ O‘zingizga nikoh taklifi yubora olmaysiz."
        )
        return

    sender_family = await get_family(sender_id)

    if sender_family is not None:
        await message.answer(
            "❌ Siz allaqachon nikohdasiz."
        )
        return

    receiver_family = await get_family(receiver_id)

    if receiver_family is not None:
        await message.answer(
            "❌ Bu foydalanuvchi allaqachon nikohda."
        )
        return

    existing = await get_pending_family_proposal(
        sender_id,
        receiver_id,
    )

    if existing is not None:
        await message.answer(
            "⏳ Bu foydalanuvchiga allaqachon nikoh taklifi yuborilgansiz."
        )
        return

    reverse = await get_pending_family_proposal(
        receiver_id,
        sender_id,
    )

    if reverse is not None:
        await message.answer(
            "❤️ Sizga bu foydalanuvchidan allaqachon "
            "nikoh taklifi kelgan."
        )
        return

    proposal_id = await create_family_proposal(
        sender_id,
        receiver_id,
    )

    if proposal_id is None:
        await message.answer(
            "❌ Nikoh taklifini yaratib bo‘lmadi."
        )
        return

    sender_name = (
        message.from_user.full_name
        or "O‘yinchi"
    )

    receiver_name = (
        target.full_name
        or "O‘yinchi"
    )

    await message.answer(
        "💍 <b>THRONE — NIKOH TAKLIFI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"❤️ <b>{sender_name}</b>\n"
        "sizga\n"
        f"💍 <b>{receiver_name}</b>\n"
        "nikoh taklifini yubordi.\n\n"
        "🤝 Qaroringizni tanlang:",
        reply_markup=proposal_keyboard(proposal_id),
    )


# ============================================================
# ACCEPT
# ============================================================

@router.callback_query(
    F.data.startswith("family_accept:")
)
async def family_accept_callback(callback: CallbackQuery):
    try:
        proposal_id = int(
            callback.data.split(":", 1)[1]
        )
    except (ValueError, AttributeError):
        await callback.answer(
            "❌ Taklif ma'lumotida xatolik.",
            show_alert=True,
        )
        return

    proposal = await get_family_proposal(proposal_id)

    if proposal is None:
        await callback.answer(
            "❌ Bu taklif topilmadi.",
            show_alert=True,
        )
        return

    receiver_id = proposal["receiver_id"]
    sender_id = proposal["sender_id"]

    # Faqat taklif qabul qiluvchisi qabul qila oladi.
    if callback.from_user.id != receiver_id:
        await callback.answer(
            "❌ Bu taklif siz uchun emas.",
            show_alert=True,
        )
        return

    if proposal["status"] != "pending":
        await callback.answer(
            "❌ Bu taklif allaqachon yopilgan.",
            show_alert=True,
        )
        return

    sender_family = await get_family(sender_id)
    receiver_family = await get_family(receiver_id)

    if sender_family is not None or receiver_family is not None:
        await update_family_proposal(
            proposal_id,
            "rejected",
        )

        await callback.answer(
            "❌ Nikoh amalga oshmadi. Tomonlardan biri allaqachon nikohda.",
            show_alert=True,
        )
        return

    family_id = await create_family(
        sender_id,
        receiver_id,
    )

    if family_id is None:
        await update_family_proposal(
            proposal_id,
            "rejected",
        )

        await callback.answer(
            "❌ Nikohni yaratib bo‘lmadi.",
            show_alert=True,
        )
        return

    await update_family_proposal(
        proposal_id,
        "accepted",
    )

    sender = await get_user(sender_id)
    receiver = await get_user(receiver_id)

    sender_name = (
        sender["full_name"]
        if sender
        else f"ID {sender_id}"
    )

    receiver_name = (
        receiver["full_name"]
        if receiver
        else f"ID {receiver_id}"
    )

    await callback.message.edit_text(
        "💍 <b>THRONE — NIKOH TASDIQLANDI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"❤️ <b>{sender_name}</b> va "
        f"<b>{receiver_name}</b>\n"
        "bugundan boshlab bir oilaning vakiliga aylandi.\n\n"
        "🏰 Ikki qalb — bitta xonadon.\n"
        "🤝 Birga qurilgan yo‘l, birga himoya qilinadigan oila.\n\n"
        "✨ Nikohingiz muborak bo‘lsin!\n\n"
        "👑 THRONE’da ba'zi rishtalar tojdan ham qadrli."
    )

    await callback.answer(
        "❤️ Nikoh tasdiqlandi!"
    )


# ============================================================
# REJECT
# ============================================================

@router.callback_query(
    F.data.startswith("family_reject:")
)
async def family_reject_callback(callback: CallbackQuery):
    try:
        proposal_id = int(
            callback.data.split(":", 1)[1]
        )
    except (ValueError, AttributeError):
        await callback.answer(
            "❌ Taklif ma'lumotida xatolik.",
            show_alert=True,
        )
        return

    proposal = await get_family_proposal(proposal_id)

    if proposal is None:
        await callback.answer(
            "❌ Bu taklif topilmadi.",
            show_alert=True,
        )
        return

    if callback.from_user.id != proposal["receiver_id"]:
        await callback.answer(
            "❌ Bu taklif siz uchun emas.",
            show_alert=True,
        )
        return

    if proposal["status"] != "pending":
        await callback.answer(
            "❌ Bu taklif allaqachon yopilgan.",
            show_alert=True,
        )
        return

    await update_family_proposal(
        proposal_id,
        "rejected",
    )

    await callback.message.edit_text(
        "💔 <b>THRONE — NIKOH TAKLIFI</b>\n\n"
        "Taklif rad etildi.\n\n"
        "🏰 Qirollikdagi yo‘llar ba'zan turlicha davom etadi."
    )

    await callback.answer(
        "Taklif rad etildi."
    )


# ============================================================
# PROPOSALS
# ============================================================

@router.message(Command("proposals"))
async def proposals_command(message: Message):
    user_id = message.from_user.id

    proposal = await get_pending_family_proposal(
        user_id,
        user_id,
    )

    if proposal is None:
        await message.answer(
            "💍 Sizda hozircha kutilayotgan nikoh taklifi yo‘q."
        )
        return

    await message.answer(
        "💍 <b>THRONE NIKOH TAKLIFI</b>\n\n"
        f"👤 Taklif yuboruvchi: "
        f"<code>{proposal['sender_id']}</code>\n\n"
        "Taklifni guruhdagi xabardan boshqaring."
  )
