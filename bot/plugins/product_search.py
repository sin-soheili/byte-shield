from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import ExternalUrlInvalid, RPCError
from .api import get_product_by_slug
import os
from collections import defaultdict
from .buttons import back_to_start
from .utils import find_local_image

def Tree():
    return defaultdict(Tree)

user_pocket = Tree()

# Callback handler for the search button
@Client.on_callback_query(filters.regex("^search_product$"))
async def search_product_callback(client, callback_query):
    await callback_query.message.reply("لطفا اسلاگ محصول را وارد کنید:")
    user_pocket['step']['product_search'][callback_query.from_user.id] = "waiting_slug"
    await callback_query.answer()

# Create a filter for the slug input
def is_waiting_slug(_, __, message: Message):
    return user_pocket['step']['product_search'].get(message.from_user.id) == "waiting_slug"

# Message handler for slug input
@Client.on_message(filters.text & filters.private & filters.create(is_waiting_slug))
async def handle_slug_message(client, message: Message):
    slug = message.text.strip()
    product = get_product_by_slug(slug)
    if product:
        text = (
            f"📦 <b>{product['name']}</b>\n"
            f"📝 توضیحات: {product['description']}\n"
            f"💰 قیمت: {product['price']} تومان"
        )
        product_url = f"http://127.0.0.1:8000/products/{product['id']}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("👁️ مشاهده در سایت", url=product_url)],
            [InlineKeyboardButton("🔄 بازگشت به منو", callback_data="main_menu")]
        ])
        image_sent = False
        if product.get('image'):
            image_url = f"http://127.0.0.1:8000{product['image']}"
            try:
                await message.reply_photo(photo=image_url, caption=text, reply_markup=keyboard)
                image_sent = True
            except RPCError:
                local_path = find_local_image(product['image'])
                if local_path:
                    try:
                        await message.reply_photo(photo=local_path, caption=text, reply_markup=keyboard)
                        image_sent = True
                    except Exception:
                        pass
        if not image_sent:
            await message.reply(text, reply_markup=keyboard)
    else:
        await message.reply("❌ محصولی با این اسلاگ پیدا نشد!", reply_markup=back_to_start())
    # Reset state
    user_pocket['step']['product_search'][message.from_user.id] = "start_state"

