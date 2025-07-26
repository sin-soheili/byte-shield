from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from collections import defaultdict
from .database import add_channel, get_active_channels, get_all_product_messages
from .buttons import back_to_start

# Data structure for tracking user states
user_state = defaultdict(lambda: defaultdict(str))

def waiting_channel_select_filter(_, __, message: Message):
    return user_state['channel_selection'].get(message.from_user.id) == "waiting_channel_select"

def waiting_channel_add_filter(_, __, message: Message):
    return user_state['channel_selection'].get(message.from_user.id) == "waiting_channel_add"

@Client.on_callback_query(filters.regex("^change_default_channel$"))
async def change_default_channel(client: Client, callback_query: CallbackQuery):
    """Handle the callback for changing the default channel"""
    # Get current channels
    channels = get_active_channels()
    
    keyboard = []
    if channels:
        for channel_id, channel_username in channels:
            keyboard.append([
                InlineKeyboardButton(
                    f"@{channel_username}",
                    callback_data=f"select_channel_{channel_id}"
                )
            ])
    
    keyboard.append([InlineKeyboardButton("➕ افزودن کانال جدید", callback_data="add_new_channel")])
    keyboard.append([InlineKeyboardButton("🔙 بازگشت", callback_data="back_to_main")])
    
    # Set user state to waiting for channel selection
    user_state['channel_selection'][callback_query.from_user.id] = "waiting_channel_select"
    
    await callback_query.edit_message_text(
        "لطفا کانال پیش‌فرض جدید را انتخاب کنید یا یک کانال جدید اضافه کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

@Client.on_callback_query(filters.regex("^add_new_channel$"))
async def add_new_channel(client: Client, callback_query: CallbackQuery):
    """Handle the callback for adding a new channel"""
    user_state['channel_selection'][callback_query.from_user.id] = "waiting_channel_add"
    
    await callback_query.edit_message_text(
        "لطفا آدرس کانال را به صورت @channel_name ارسال کنید:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 بازگشت", callback_data="change_default_channel")]
        ])
    )

@Client.on_message(filters.text & filters.create(waiting_channel_add_filter))
async def handle_channel_add(client: Client, message: Message):
    """Handle channel addition"""
    channel_username = message.text.strip()
    
    if not channel_username.startswith('@'):
        await message.reply_text(
            "لطفا آدرس کانال را با @ شروع کنید.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="change_default_channel")]
            ])
        )
        return
    
    try:
        # Try to get channel info from Telegram
        channel = await client.get_chat(channel_username)
        
        # Add channel to database
        add_channel(channel.id, channel_username[1:])  # Remove @ from username
        
        # Clear the user state
        user_state['channel_selection'].pop(message.from_user.id, None)
        
        await message.reply_text(
            f"کانال {channel_username} با موفقیت اضافه شد.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="change_default_channel")]
            ])
        )
    except Exception as e:
        await message.reply_text(
            "خطا در افزودن کانال. لطفا مطمئن شوید که:\n"
            "1. آدرس کانال صحیح است\n"
            "2. ربات در کانال ادمین است\n"
            "3. کانال عمومی است",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 بازگشت", callback_data="change_default_channel")]
            ])
        )

@Client.on_callback_query(filters.regex("^select_channel_"))
async def select_channel(client: Client, callback_query: CallbackQuery):
    """Handle the callback for selecting a specific channel"""
    # Extract channel_id from callback data
    channel_id = int(callback_query.data.split('_')[-1])
    
    # Get channel info from the list of active channels
    channels = get_active_channels()
    selected_channel = next((ch for ch in channels if ch[0] == channel_id), None)
    
    if not selected_channel:
        await callback_query.edit_message_text(
            "کانال مورد نظر یافت نشد.",
            reply_markup=back_to_start()
        )
        return
    
    # Store the selected channel in user data
    client.default_channel = {
        'channel_id': channel_id,
        'channel_username': selected_channel[1]
    }
    
    # Clear the user state
    user_state['channel_selection'].pop(callback_query.from_user.id, None)
    
    await callback_query.edit_message_text(
        f"کانال پیش‌فرض به @{selected_channel[1]} تغییر یافت.",
        reply_markup=back_to_start()
    )

@Client.on_message(filters.text & filters.create(waiting_channel_select_filter))
async def handle_channel_input(client: Client, message: Message):
    """Handle text input when waiting for channel selection"""
    # Clear the user state
    user_state['channel_selection'].pop(message.from_user.id, None)
    
    await message.reply_text(
        "لطفا از دکمه‌های موجود برای انتخاب کانال استفاده کنید.",
        reply_markup=back_to_start()
    ) 