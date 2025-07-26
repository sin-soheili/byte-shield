from pyrogram import Client, filters
from pyrogram.types import Message
from config import API_ID, API_HASH, BOT_TOKEN
from plugins.database import initialize_db
from plugins.product_updater import register_handlers as register_product_updater


app = Client(
    name="byteshield",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="plugins")
)

initialize_db()
register_product_updater(app)

app.run()