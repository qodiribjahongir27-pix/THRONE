import asyncio

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from database import init_db

from handlers.start import router as start_router
from handlers.profile import router as profile_router
from handlers.economy import router as economy_router
from handlers.kingdom import router as kingdom_router
from handlers.clan import router as clan_router
from handlers.family import router as family_router
from handlers.game import router as game_router


dp = Dispatcher()


async def main():
    # Ma'lumotlar bazasini ishga tushirish
    await init_db()

    # Bot
    bot = Bot(token=BOT_TOKEN)

    # Routerlar
    dp.include_router(start_router)
    dp.include_router(profile_router)
    dp.include_router(economy_router)
    dp.include_router(kingdom_router)
    dp.include_router(clan_router)
    dp.include_router(family_router)
    dp.include_router(game_router)

    print("👑 THRONE bot ishga tushdi...")

    # Botni ishga tushirish
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
