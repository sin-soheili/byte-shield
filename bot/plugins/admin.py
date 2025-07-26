from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message
from .database import cursor, get_all_users
from .buttons import back_to_start
from collections import defaultdict

def Tree():
    return defaultdict(Tree)

user_pocket = Tree()
MAX_MESSAGE_LENGTH = 4000


@Client.on_callback_query(filters.regex("^list_users$"))
async def list_users_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id != 6698126269:
        await callback_query.answer("❌ شما اجازه دسترسی به این بخش را ندارید.", show_alert=True)
        return

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    if not users:
        await callback_query.message.reply_text("هیچ کاربری ثبت نشده است.")
        return

    response = "👥 **لیست کاربران:**\n\n"
    for user in users:
        response += f"🆔 `{user[0]}` | @{user[1]} | {user[2]} {user[3]}\n"

    total_users = len(users)
    response += f"\n📊 **تعداد کل کاربران:** {total_users}"

    messages = []
    while len(response) > MAX_MESSAGE_LENGTH:
        split_index = response.rfind("\n", 0, MAX_MESSAGE_LENGTH)
        if split_index == -1:
            split_index = MAX_MESSAGE_LENGTH
        messages.append(response[:split_index])
        response = response[split_index:]

    messages.append(response)

    for part in messages:
        await callback_query.message.reply(part)

    await callback_query.message.reply("✅ عملیات پایان یافت.", reply_markup=back_to_start())


@Client.on_callback_query(filters.regex("^broadcast$"))
async def broad_cast_handler(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    user_pocket['step']['admin'][user_id] = "waiting_broadcast"

    await callback_query.message.reply_text("لطفا پیام همگانی خود را ارسال کنید!\n\nبرای کنسل کردن، /cancel را بفرستید.")


def is_waiting_broadcast(_, __, message: Message):
    return user_pocket['step']['admin'].get(message.from_user.id) == "waiting_broadcast"


@Client.on_message(filters.create(is_waiting_broadcast))
async def broad_cast_message(client: Client, message: Message):
    user_id = message.from_user.id

    if message.text == "/cancel":
        user_pocket['step']['admin'][user_id] = "start_state"
        await message.reply("با موفقیت کنسل شد", reply_markup=back_to_start())
        return

    user_list = get_all_users()
    success_count = 0
    failed_count = 0

    for user_id in user_list:
        try:
            await client.send_message(chat_id=user_id, text=message.text)
            success_count += 1
        except Exception:
            failed_count += 1

    user_pocket['step']['admin'][message.from_user.id] = "start_state"

    await message.reply(
        f"پیام همگانی با موفقیت ارسال شد!\n"
        f"✅ تعداد موفق: {success_count}\n"
        f"❌ تعداد ناموفق: {failed_count}",
        reply_markup=back_to_start()
    )
