import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
CREATOR_ID = int(os.getenv("CREATOR_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN Railway Variables ichida topilmadi")
