from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.errors import RPCError
from collections import defaultdict
from .buttons import latest_products_buttons
from .api import get_categories, get_products_by_category, get_latest_products
from .utils import find_local_image

# Data structure for tracking user states
user_state = defaultdict(lambda: defaultdict(str))

# Function to send product messages
async def send_product_message(client, message: Message, products: list):
    """Send product messages with image (if available) and view button"""
    for product in products[:5]:
        text = (
            f"📦 <b>{product['name']}</b>\n"
            f"📝 توضیحات: {product['description']}\n"
            f"💰 قیمت: {product['price']:,} تومان"
        )
        product_url = f"http://127.0.0.1:8000/products/{product['id']}"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 مشاهده در سایت", url=product_url)]
        ])
        image_sent = False
        if product.get('image'):
            image_url = f"http://127.0.0.1:8000{product['image']}"
            try:
                await message.reply_photo(
                    photo=image_url,
                    caption=text,
                    reply_markup=keyboard
                )
                image_sent = True
            except RPCError:
                local_path = find_local_image(product['image'])
                if local_path:
                    try:
                        await message.reply_photo(
                            photo=local_path,
                            caption=text,
                            reply_markup=keyboard
                        )
                        image_sent = True
                    except Exception:
                        pass
        if not image_sent:
            await message.reply(text, reply_markup=keyboard)

# Filter for category selection
def waiting_category_select_filter(_, __, message: Message):
    return user_state['latest_products_by_category'].get(message.from_user.id) == "waiting_category_select"

# Filter for category products
def waiting_category_products_filter(_, __, message: Message):
    return user_state['latest_products_by_category'].get(message.from_user.id) == "waiting_category_products"

# Handler for latest products button
@Client.on_callback_query(filters.regex(r"^latest_products$"))
async def latest_products_callback(client, callback_query: CallbackQuery):
    await callback_query.message.reply("📦 محصولات اخیر را چگونه مشاهده کنیم؟", reply_markup=latest_products_buttons())
    await callback_query.answer()

# Handler for latest products by time
@Client.on_callback_query(filters.regex(r"^latest_products_by_time$"))
async def latest_products_by_time(client, callback_query: CallbackQuery):
    products = get_latest_products()
    if not products:
        await callback_query.message.reply("❌ هیچ محصول جدیدی یافت نشد!")
    else:
        await send_product_message(client, callback_query.message, products)
    await callback_query.answer()

# Handler for latest products by category
@Client.on_callback_query(filters.regex(r"^latest_products_by_category$"))
async def latest_products_by_category(client, callback_query: CallbackQuery):
    categories = get_categories()
    if not categories:
        await callback_query.message.reply("❌ هیچ دسته‌بندی‌ای یافت نشد!")
        await callback_query.answer()
        return
    buttons = [
        [InlineKeyboardButton(f"📂 {cat['title']}", callback_data=f"show_category_{cat['id']}")]
        for cat in categories
    ]
    await callback_query.message.reply(
        "📚 یک دسته‌بندی انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()

# Handler for showing products of a category
@Client.on_callback_query(filters.regex(r"^show_category_(\d+)$"))
async def show_category_products(client, callback_query: CallbackQuery):
    import re
    match = re.match(r"^show_category_(\d+)$", callback_query.data)
    if not match:
        await callback_query.answer("❌ دسته‌بندی نامعتبر!", show_alert=True)
        return
    category_id = match.group(1)
    products = get_products_by_category(category_id)
    if not products:
        await callback_query.message.reply("❌ هیچ محصولی در این دسته‌بندی یافت نشد!")
    else:
        await send_product_message(client, callback_query.message, products)
    await callback_query.answer()