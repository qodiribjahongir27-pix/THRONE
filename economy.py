from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import CREATOR_ID
from database import (
    get_user,
    create_user,
    get_balance,
    update_balance,
    spend_balance,
    security_log,
)


router = Router()


CURRENCIES = {
    "gold": "🟡 Oltin",
    "coin": "🪙 Coin",
    "diamond": "💎 Olmos",
}


def is_creator(user_id: int) -> bool:
    return user_id == CREATOR_ID


def format_balance(user_id: int, currency: str, amount: int) -> str:
    if is_creator(user_id):
        return "∞"

    return f"{amount:,}".replace(",", " ")


async def ensure_user(message: Message):
    user = await get_user(message.from_user.id)

    if user is None:
        await create_user(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or "O‘yinchi",
        )

        user = await get_user(message.from_user.id)

    return user


def wallet_text(user_id: int, user) -> str:
    if is_creator(user_id):
        gold = "∞"
        coin = "∞"
        diamond = "∞"
        elite = "AKTIV ∞"
    else:
        gold = format_balance(
            user_id,
            "gold",
            user["gold"] or 0,
        )

        coin = format_balance(
            user_id,
            "coin",
            user["coin"] or 0,
        )

        diamond = format_balance(
            user_id,
            "diamond",
            user["diamond"] or 0,
        )

        elite = (
            "AKTIV"
            if user["elite"]
            else "FAOL EMAS"
        )

    return (
        "💰 <b>THRONE HAMYONI</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🟡 Oltin: <b>{gold}</b>\n"
        f"🪙 Coin: <b>{coin}</b>\n"
        f"💎 Olmos: <b>{diamond}</b>\n\n"
        f"⚜️ Elite Pass: <b>{elite}</b>"
    )


@router.callback_query(F.data == "wallet")
async def wallet_callback(callback: CallbackQuery):
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
            "Hamyonni yuklashda xatolik.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        wallet_text(user_id, user)
    )

    await callback.answer()


@router.message(Command("wallet"))
async def wallet_command(message: Message):
    user = await ensure_user(message)

    if user is None:
        await message.answer(
            "Profilni yaratishda xatolik yuz berdi."
        )
        return

    await message.answer(
        wallet_text(message.from_user.id, user)
    )


@router.message(Command("gold"))
async def gold_command(message: Message):
    user = await ensure_user(message)

    if user is None:
        await message.answer(
            "Profilni yaratishda xatolik yuz berdi."
        )
        return

    user_id = message.from_user.id

    if is_creator(user_id):
        amount = "∞"
    else:
        amount = format_balance(
            user_id,
            "gold",
            user["gold"] or 0,
        )

    await message.answer(
        f"🟡 <b>Oltin</b>\n\n"
        f"Sizning oltiningiz: <b>{amount}</b>"
    )


@router.message(Command("coin"))
async def coin_command(message: Message):
    user = await ensure_user(message)

    if user is None:
        await message.answer(
            "Profilni yaratishda xatolik yuz berdi."
        )
        return

    user_id = message.from_user.id

    if is_creator(user_id):
        amount = "∞"
    else:
        amount = format_balance(
            user_id,
            "coin",
            user["coin"] or 0,
        )

    await message.answer(
        f"🪙 <b>Coin</b>\n\n"
        f"Sizning Coin'ingiz: <b>{amount}</b>"
    )


@router.message(Command("diamond"))
async def diamond_command(message: Message):
    user = await ensure_user(message)

    if user is None:
        await message.answer(
            "Profilni yaratishda xatolik yuz berdi."
        )
        return

    user_id = message.from_user.id

    if is_creator(user_id):
        amount = "∞"
    else:
        amount = format_balance(
            user_id,
            "diamond",
            user["diamond"] or 0,
        )

    await message.answer(
        f"💎 <b>Olmos</b>\n\n"
        f"Sizning olmosingiz: <b>{amount}</b>"
    )


@router.message(Command("transfer"))
async def transfer_command(message: Message):
    parts = message.text.split()

    if len(parts) != 4:
        await message.answer(
            "❌ Foydalanish:\n\n"
            "<code>/transfer USER_ID VALYUTA MIQDOR</code>\n\n"
            "Masalan:\n"
            "<code>/transfer 123456789 gold 500</code>\n\n"
            "Valyutalar:\n"
            "🟡 gold\n"
            "🪙 coin\n"
            "💎 diamond"
        )
        return

    try:
        receiver_id = int(parts[1])
        currency = parts[2].lower()
        amount = int(parts[3])
    except ValueError:
        await message.answer(
            "❌ USER_ID va MIQDOR raqam bo‘lishi kerak."
        )
        return

    sender_id = message.from_user.id

    if receiver_id == sender_id:
        await message.answer(
            "❌ O‘zingizga resurs yubora olmaysiz."
        )
        return

    if currency not in CURRENCIES:
        await message.answer(
            "❌ Noto‘g‘ri valyuta.\n\n"
            "🟡 gold\n"
            "🪙 coin\n"
            "💎 diamond"
        )
        return

    if amount <= 0:
        await message.answer(
            "❌ Miqdor 0 dan katta bo‘lishi kerak."
        )
        return

    receiver = await get_user(receiver_id)

    if receiver is None:
        await message.answer(
            "❌ Bu foydalanuvchi THRONE’da topilmadi."
        )
        return

    if is_creator(sender_id):
        await update_balance(
            receiver_id,
            currency,
            amount,
        )

        await security_log(
            sender_id,
            "creator_transfer",
            (
                f"receiver={receiver_id}; "
                f"currency={currency}; "
                f"amount={amount}"
            ),
        )

        await message.answer(
            "👑 <b>THRONE YARATUVCHI</b>\n\n"
            f"{CURRENCIES[currency]}: "
            f"<b>{amount:,}</b>\n"
            f"👤 Qabul qiluvchi: <code>{receiver_id}</code>\n\n"
            "✅ Resurs yuborildi."
        )

        return

    sender_balance = await get_balance(
        sender_id,
        currency,
    )

    if sender_balance < amount:
        await message.answer(
            f"❌ Sizda yetarli "
            f"{CURRENCIES[currency]} mavjud emas."
        )
        return

    success = await spend_balance(
        sender_id,
        currency,
        amount,
    )

    if not success:
        await message.answer(
            "❌ Transfer amalga oshmadi. "
            "Balansingiz o‘zgargan bo‘lishi mumkin."
        )
        return

    await update_balance(
        receiver_id,
        currency,
        amount,
    )

    await security_log(
        sender_id,
        "transfer",
        (
            f"receiver={receiver_id}; "
            f"currency={currency}; "
            f"amount={amount}"
        ),
    )

    await message.answer(
        "💸 <b>TRANSFER AMALGA OSHIRILDI</b>\n\n"
        f"👤 Qabul qiluvchi: <code>{receiver_id}</code>\n"
        f"{CURRENCIES[currency]}: "
        f"<b>{amount:,}</b>\n\n"
        "✅ Resurs muvaffaqiyatli yuborildi."
    )


@router.callback_query(F.data == "economy")
async def economy_callback(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)

    if user is None:
        await create_user(
            user_id=callback.from_user.id,
            username=callback.from_user.username or "",
            full_name=callback.from_user.full_name or "O‘yinchi",
        )

        user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "Iqtisod tizimini yuklashda xatolik.",
            show_alert=True,
        )
        return

    await callback.message.edit_text(
        wallet_text(
            callback.from_user.id,
            user,
        )
    )

    await callback.answer()
