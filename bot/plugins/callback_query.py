from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from .buttons import back_to_start, get_menu_buttons
from .utils import clear_user_state


@Client.on_callback_query(filters.regex("main_menu"))
async def upload_handler(client: Client, callback: CallbackQuery):
    user_id = callback.from_user.id
    clear_user_state(user_id)
    await callback.message.reply_text(
        text="با موفقیت به منوی اصلی بازگشتید:)", reply_markup=get_menu_buttons(user_id)
    )

