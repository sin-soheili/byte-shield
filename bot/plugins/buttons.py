from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config import ADMINS


def get_menu_buttons(user_id):
    buttons = [
        [InlineKeyboardButton("🔍 جستجوی محصول", callback_data="search_product")],
        [InlineKeyboardButton("🆕 محصولات اخیر", callback_data="latest_products")],
        [InlineKeyboardButton("👁️ پیگیری سفارش ", callback_data="orders")],
        [InlineKeyboardButton("💬 ثبت بازخورد ناشناس", callback_data="send_feedback")],
        [InlineKeyboardButton("👨‍💻 درباره توسعه‌دهنده", callback_data="about_dev")],
    ]

    if user_id in ADMINS:
        buttons += admin_panel_buttons(raw=True)

    return InlineKeyboardMarkup(buttons)


def admin_panel_buttons(raw=False):
    buttons = [
        [InlineKeyboardButton("📢 تغییر کانال پیش‌فرض", callback_data="change_default_channel")],
        [ 
        InlineKeyboardButton("📢 ارسال پیام همگانی", callback_data="broadcast"),
        InlineKeyboardButton("👥 مشاهده اعضا", callback_data="list_users")
        ]
    ]
    return buttons if raw else InlineKeyboardMarkup(buttons)

def latest_products_buttons():
    buttons = [
        [InlineKeyboardButton("🆕 براساس دسته‌بندی", callback_data="latest_products_by_category")],
        [InlineKeyboardButton("🆕 براساس زمان", callback_data="latest_products_by_time")],
    ]
    return InlineKeyboardMarkup(buttons)

def back_to_start():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 بازگشت به منوی اصلی", callback_data="main_menu")]])
