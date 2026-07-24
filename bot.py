import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# ==========================
# SOZLAMALAR
# ==========================

BOT_TOKEN = "8288853849:AAFfJaYec6NgTldlZp2R7svby5iSLc8lB8E"
ADMIN_ID = 6401247171

FORCE_CHANNELS = [
    "@VIP_drama_uz01",
    "@trend_muzikalar_uz_01"
]

MOVIE_CHANNEL = "@daxshat_kinolar_uzzz"

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# ==========================
# DATABASE
# ==========================

db = sqlite3.connect("database.db")
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY
)
""")

sql.execute("""
CREATE TABLE IF NOT EXISTS movies(
code TEXT PRIMARY KEY,
message_id INTEGER
)
""")

db.commit()

# ==========================
# USER SAQLASH
# ==========================

def add_user(user_id):
    sql.execute("SELECT * FROM users WHERE id=?", (user_id,))
    if sql.fetchone() is None:
        sql.execute(
            "INSERT INTO users VALUES(?)",
            (user_id,)
        )
        db.commit()

# ==========================
# START
# ==========================

@dp.message(CommandStart())
async def start(message: Message):

    add_user(message.from_user.id)

    text = f"""
Assalomu alaykum <b>{message.from_user.full_name}</b> 👋

🎬 Kino kodini yuboring.

Bot orqali kerakli kinoni olishingiz mumkin.
"""

    await message.answer(text)
