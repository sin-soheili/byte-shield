from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import RPCError
import aiohttp
import json
import os
from .database import save_product_message, get_product_message, get_active_channels, get_all_product_messages, delete_product_message
from .buttons import back_to_start
from .utils import find_local_image
from .api import PRODUCTS_API, PRODUCTS_PAGE
from config import ADMINS

async def fetch_products(api_url: str) -> list:
    """Fetch products from the API"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
                print(f"API Error: Status {response.status}")  # Debug log
                return []
    except Exception as e:
        print(f"API Connection Error: {e}")  # Debug log
        return []

async def send_product_message(client: Client, chat_id: str, product: dict) -> int:
    """Send product message with image (if available) and view button"""
    text = (
        f"📦 <b>{product['name']}</b>\n"
        f"📝 توضیحات: {product['description']}\n"
        f"💰 قیمت: {product['price']:,} تومان"
    )
    product_url = f"{PRODUCTS_PAGE}/{product['id']}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 مشاهده در سایت", url=product_url)]
    ])

    image_sent = False
    if product.get('image'):
        try:
            sent_message = await client.send_photo(
                chat_id=chat_id,
                photo=product['image'],
                caption=text,
                reply_markup=keyboard
            )
            image_sent = True
            return sent_message.id
        except RPCError:
            local_path = find_local_image(product['image'])
            if local_path:
                try:
                    sent_message = await client.send_photo(
                        chat_id=chat_id,
                        photo=local_path,
                        caption=text,
                        reply_markup=keyboard
                    )
                    image_sent = True
                    return sent_message.id
                except Exception:
                    pass
    
    if not image_sent:
        sent_message = await client.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard
        )
        return sent_message.id

async def remove_deleted_products(client: Client, channel_username: str, channel_id: int, api_products: list) -> int:
    """Remove products from channel that no longer exist in API"""
    removed_count = 0
    # Get all product messages for this channel
    channel_messages = get_all_product_messages()
    
    # Create set of product IDs from API
    api_product_ids = {product['id'] for product in api_products}
    
    # Check each message in channel
    for product_id, msg_channel_id, message_id, _ in channel_messages:
        if msg_channel_id == channel_id and product_id not in api_product_ids:
            try:
                # Delete message from channel
                await client.delete_messages(
                    chat_id=channel_username,
                    message_ids=message_id
                )
                # Remove from database
                delete_product_message(product_id, channel_id)
                removed_count += 1
            except Exception as e:
                print(f"Error removing product {product_id} from channel {channel_username}: {e}")
    
    return removed_count

async def update_products(client: Client, message: Message):
    """Update products from the API"""
    # API endpoint for products
    api_url = PRODUCTS_API
    
    # Send initial message
    status_message = await message.reply_text("در حال دریافت محصولات از سرور...")
    
    try:
        # Fetch products from API
        products = await fetch_products(api_url)
        
        # Get active channel
        channels = get_active_channels()
        if not channels:
            await status_message.reply_text(
                "هیچ کانالی برای ارسال محصولات تنظیم نشده است.",
                reply_markup=back_to_start()
            )
            return
        
        # Get the first active channel (default channel)
        channel_id, channel_username = channels[0]
        
        # First, remove products that no longer exist
        removed_count = await remove_deleted_products(client, channel_username, channel_id, products)
        
        # Counter for new products
        new_products = 0
        
        # Process each product
        for product in products:
            # Check if product already exists in channel
            existing_message = get_product_message(product['id'], channel_id)
            
            if not existing_message:
                try:
                    # Send product message with image
                    message_id = await send_product_message(client, channel_username, product)
                    
                    # Save message ID in database
                    save_product_message(product['id'], channel_id, message_id)
                    new_products += 1
                    
                except Exception as e:
                    print(f"Error sending product to channel {channel_username}: {e}")
        
        # Update status message
        status_text = f"✅ به‌روزرسانی با موفقیت انجام شد.\n"
        if new_products > 0:
            status_text += f"📦 {new_products} محصول جدید به کانال @{channel_username} اضافه شد.\n"
        if removed_count > 0:
            status_text += f"🗑️ {removed_count} محصول حذف شده از کانال @{channel_username} حذف شد."
        
        await status_message.reply_text(
            status_text,
            reply_markup=back_to_start()
        )
        
    except Exception as e:
        await status_message.reply_text(
            f"❌ خطا در به‌روزرسانی محصولات:\n{str(e)}",
            reply_markup=back_to_start()
        )

def register_handlers(client: Client):
    """Register product update handlers"""
    @client.on_message(filters.command("update"))
    async def update_command(client: Client, message: Message):
        if message.from_user.id in ADMINS:
            await update_products(client, message)
        else:
            await message.reply_text("شما اجازه دسترسی به این دستور را ندارید.")