from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from .buttons import back_to_start
from config import ADMINS
from collections import defaultdict

def Tree():
    return defaultdict(Tree)

user_pocket = Tree()


@Client.on_callback_query(filters.regex("send_feedback"))
async def start_feedback_handler(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    user_pocket["step"]["feedback"][user_id] = "waiting_feedback"

    await callback.message.reply_text(
        "📝 لطفا بازخورد خود را بنویسید و ارسال کنید.\n\nبرای لغو، /cancel را بفرستید.",
        reply_markup=back_to_start()
    )


def is_waiting_feedback(_, client: Client, message: Message):
    return user_pocket["step"]["feedback"].get(message.from_user.id) == "waiting_feedback"


@Client.on_message(filters.create(is_waiting_feedback))
async def receive_feedback_handler(client: Client, message: Message):
    user_id = message.from_user.id

    if message.text.strip() == "/cancel":
        user_pocket["step"]["feedback"][user_id] = None
        await message.reply_text("❌ عملیات لغو شد.", reply_markup=back_to_start())
        return

    feedback_text = message.text

    for admin_id in ADMINS:
        try:
            await client.send_message(admin_id, f"📩 بازخورد ناشناس:\n\n{feedback_text}")
        except Exception as e:
            print(f"خطا در ارسال بازخورد به {admin_id}: {e}")

    user_pocket["step"]["feedback"][user_id] = None
    await message.reply_text("✅ بازخورد شما با موفقیت ارسال شد. ممنون از همراهی‌تان!", reply_markup=back_to_start())
