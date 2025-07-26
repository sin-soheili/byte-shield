from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from .buttons import back_to_start, get_menu_buttons


@Client.on_callback_query(filters.regex("about_dev"))
async def about_dev_handler(client: Client, callback: CallbackQuery):

    text = """
👨‍💻 درباره من:
سلام! من یک توسعه‌دهنده پرانرژی و عاشق کدنویسی هستم که همیشه دنبال یادگیری و کشف چالش‌های جدیده. به دنیای برنامه‌نویسی از همون روزای اول با اشتیاق وارد شدم و حالا بعد از چند سال تجربه، روی پروژه‌های مختلفی از توسعه وب گرفته تا امنیت و بات‌های تلگرامی کار کردم. 🚀

💡 مهارت‌های من:
🔹 Python (FastAPI, Django, Flask, asyncio, Telethon, Pyrogram, yt-dlp)
🔹 امنیت (تست نفوذ، کار با پروکسی‌ها، مدیریت کوکی‌ها، Web Scraping حرفه‌ای)
🔹 توسعه وب (HTML, CSS, JavaScript, Tailwind, Alpine.js, Vue)
🔹 مدیریت دیتابیس (PostgreSQL, SQLite, Redis)
🔹 خودکارسازی و Web Scraping (سلنیوم، BS4، REST API)

💬 من عاشق حل مسائل پیچیده و بهینه‌سازی سیستم‌ها هستم. اگه دنبال کسی هستی که بتونه یک پروژه رو از صفر تا صد اجرا کنه، من اینجام! 😉
"""

    await callback.message.reply_text(
        text=text,
        reply_markup=back_to_start()
    )
