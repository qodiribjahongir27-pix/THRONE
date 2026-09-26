from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👤 KABINET", callback_data="cabinet"),
                InlineKeyboardButton(text="🏰 QIROLLIGIM", callback_data="kingdom"),
            ],
            [
                InlineKeyboardButton(text="🎒 INVENTAR", callback_data="inventory"),
                InlineKeyboardButton(text="💰 DO‘KON", callback_data="shop"),
            ],
            [
                InlineKeyboardButton(text="🏴 KLANIM", callback_data="clan"),
                InlineKeyboardButton(text="❤️ OILA", callback_data="family"),
            ],
            [
                InlineKeyboardButton(text="⚔️ KUCHLARIM", callback_data="army"),
                InlineKeyboardButton(text="🏆 MUSOBAQALAR", callback_data="tournaments"),
            ],
            [
                InlineKeyboardButton(text="🎭 ROLLAR", callback_data="roles"),
                InlineKeyboardButton(text="📊 REYTING", callback_data="ranking"),
            ],
            [
                InlineKeyboardButton(text="🎁 BONUSLAR", callback_data="rewards"),
                InlineKeyboardButton(text="🕶️ QORA BOZOR", callback_data="black_market"),
            ],
            [
                InlineKeyboardButton(text="⚜️ THRONE ELITE", callback_data="elite"),
            ],
            [
                InlineKeyboardButton(text="🌐 TIL", callback_data="language"),
                InlineKeyboardButton(text="🤖 THRONE AI", callback_data="ai"),
            ],
            [
                InlineKeyboardButton(text="❓ YORDAM", callback_data="help"),
                InlineKeyboardButton(text="⚙️ SOZLAMALAR", callback_data="settings"),
            ],
        ]
    )
def language_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O‘zbek", callback_data="lang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang_ru"),
            ],
            [
                InlineKeyboardButton(text="🇬🇧 English", callback_data="lang_en"),
                InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="lang_tr"),
            ],
            [
                InlineKeyboardButton(text="🇸🇦 العربية", callback_data="lang_ar"),
                InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="lang_ky"),
            ],
            [
                InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_main"),
            ],
        ]
    )
