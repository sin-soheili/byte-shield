from pyrogram import Client, filters
from pyrogram.types import Message
from .buttons import get_menu_buttons
from .database import save_user


@Client.on_message(filters.command("start"))
async def start_command(client:Client, message:Message):
    text = (
        "سلام! 👋\n"
        "به ربات **ByteShield | بایت‌شیلد ** خوش آمدید. 🎉\n\n"
        "🤖 این ربات دو قابلیت اصلی دارد:\n"
        "1️⃣ ارسال خودکار محصولات دریافتی به کانال مربوطه 📤\n"
        "2️⃣ دریافت اطلاعات محصول، اطلاع‌رسانی و جستجو با کد محصول 🔍\n\n"
        "برای شروع از منوی زیر استفاده کنید 👇"
    )

    user_id = message.from_user.id
    username = message.from_user.username or "None"
    first_name = message.from_user.first_name or "None"
    last_name = message.from_user.last_name or "None"

    save_user(user_id, username, first_name, last_name)

    menu_buttons = get_menu_buttons(user_id)

    await message.reply_text(
        text=text,
        reply_markup=menu_buttons
    )
