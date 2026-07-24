import asyncio
import import
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)

# ==========================
# SOZLAMALAR
# ==========================

import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

FORCE_CHANNELS = [
    "@VIP_drama_uz01",
    "@trend_muzikalar_uz_01",
    "@Dramalar_olami_uzz"
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
# MAJBURIY OBUNA
# ==========================

SUBSCRIBE_BUTTON = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="📢 1-kanal", url="https://t.me/VIP_drama_uz01")],
        [InlineKeyboardButton(text="📢 2-kanal", url="https://t.me/trend_muzikalar_uz_01")],
        [InlineKeyboardButton(text="👥 Guruh", url="https://t.me/Dramalar_olami_uzz")],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ]
)

async def check_subscription(user_id):
    for channel in FORCE_CHANNELS:
        try:
            member = await bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True
# ==========================
# START
# ==========================

@dp.message(CommandStart())
async def start(message: Message):

    add_user(message.from_user.id)

    if not await check_subscription(message.from_user.id):

        await message.answer(
            f"""
🎬 <b>Assalomu alaykum {message.from_user.full_name}!</b>

Botdan foydalanish uchun quyidagi
2 ta kanal va 1 ta guruhga a'zo bo'ling.

👇 Obuna bo'lgach
<b>✅ Tekshirish</b> tugmasini bosing.
""",
            reply_markup=SUBSCRIBE_BUTTON
        )
        return

    await message.answer(
        f"""
🎉 Xush kelibsiz <b>{message.from_user.full_name}</b>

🎬 Endi kino kodini yuboring.
"""
    )


# ==========================
# TEKSHIRISH
# ==========================

@dp.callback_query(F.data == "check_sub")
async def check_subscribe(call: CallbackQuery):

    if await check_subscription(call.from_user.id):

        await call.message.edit_text(
            """
✅ Obuna tasdiqlandi.

🎬 Endi kino kodini yuboring.
"""
        )

    else:

        await call.answer(
            "❌ Siz hali barcha kanal va guruhlarga a'zo bo'lmagansiz!",
            show_alert=True
)

# ==========================
# ADMIN PANEL
# ==========================

admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🎬 Kino qo'shish")
        ],
        [
            KeyboardButton(text="📊 Statistika"),
            KeyboardButton(text="📢 Xabar yuborish")
        ]
    ],
    resize_keyboard=True
)


@dp.message(Command("admin"))
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "👨‍💼 Admin paneliga xush kelibsiz!",
        reply_markup=admin_menu
    )


@dp.message(F.text == "📊 Statistika")
async def statistics(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    sql.execute("SELECT COUNT(*) FROM users")

    users = sql.fetchone()[0]

    await message.answer(
        f"""
📊 BOT STATISTIKASI

👤 Foydalanuvchilar: {users} ta
"""
    )


@dp.message(F.text == "🎬 Kino qo'shish")
async def add_movie(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        """
🎬 Kino qo'shish

Quyidagi formatda yuboring:

<code>
KOD|MESSAGE_ID
</code>

Misol:

<code>
1001|25
</code>

Bu yerda:
1001 — kino kodi
25 — kino kanalidagi xabar ID si
"""
    )
# ==========================
# BROADCAST
# ==========================

broadcast_mode = False


@dp.message(F.text == "📢 Xabar yuborish")
async def broadcast(message: Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    broadcast_mode = True

    await message.answer(
        "📢 Yubormoqchi bo'lgan xabaringizni yuboring."
    )


@dp.message()
async def send_broadcast(message: Message):
    global broadcast_mode

    if message.from_user.id != ADMIN_ID:
        return

    if not broadcast_mode:
        return
    broadcast_mode = False

    sql.execute("SELECT id FROM users")
    users = sql.fetchall()

    success = 0

    for user in users:
        try:
            await bot.copy_message(
                chat_id=user[0],
                from_chat_id=message.chat.id,
                message_id=message.message_id
            )
            success += 1
        except:
            pass

    await message.answer(
        f"✅ Xabar {success} ta foydalanuvchiga yuborildi."
    )
# ==========================
# KINO SAQLASH
# ==========================

@dp.message(F.text.regexp(r"^\d+\|\d+$"))
async def save_movie(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        code, message_id = message.text.split("|")

        sql.execute(
            """
            INSERT OR REPLACE INTO movies
            (code, message_id)
            VALUES (?, ?)
            """,
            (
                code.strip(),
                int(message_id)
            )
        )

        db.commit()

        await message.answer(
            f"""
✅ Kino muvaffaqiyatli saqlandi.

🎬 Kino kodi: <code>{code}</code>

🆔 Message ID: <code>{message_id}</code>
"""
        )

    except Exception as e:

        await message.answer(
            f"❌ Xatolik:\n<code>{e}</code>"
)
        # ==========================
# KINO QIDIRISH
# ==========================

@dp.message(F.text.regexp(r"^\d+$"))
async def send_movie(message: Message):

    code = message.text.strip()

    sql.execute(
        "SELECT message_id FROM movies WHERE code=?",
        (code,)
    )

    movie = sql.fetchone()

    if movie is None:

        await message.answer(
            "❌ Bunday kodli kino topilmadi."
        )

        return

    try:

        await bot.copy_message(
            chat_id=message.from_user.id,
            from_chat_id=MOVIE_CHANNEL,
            message_id=movie[0]
        )

    except Exception as e:

        await message.answer(
            f"❌ Kino yuborishda xatolik:\n<code>{e}</code>"
        )



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())



        
    
