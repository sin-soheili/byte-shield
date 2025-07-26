import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

def initialize_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telegram_channels (
        channel_id INTEGER PRIMARY KEY,
        channel_username TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        channel_id INTEGER NOT NULL,
        message_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (channel_id) REFERENCES telegram_channels(channel_id),
        UNIQUE(product_id, channel_id)
    )
    """)
    conn.commit()

def save_user(user_id, username, first_name, last_name):
    cursor.execute("""
    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
    VALUES (?, ?, ?, ?)
    """, (user_id, username, first_name, last_name))
    conn.commit()

def get_all_users():
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    return [user[0] for user in users]

def add_channel(channel_id, channel_username):
    cursor.execute("""
    INSERT OR REPLACE INTO telegram_channels (channel_id, channel_username)
    VALUES (?, ?)
    """, (channel_id, channel_username))
    conn.commit()

def get_active_channels():
    cursor.execute("SELECT channel_id, channel_username FROM telegram_channels WHERE is_active = 1")
    return cursor.fetchall()

def save_product_message(product_id, channel_id, message_id):
    cursor.execute("""
    INSERT OR REPLACE INTO product_messages (product_id, channel_id, message_id, updated_at)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (product_id, channel_id, message_id))
    conn.commit()

def get_product_message(product_id, channel_id):
    cursor.execute("""
    SELECT message_id FROM product_messages 
    WHERE product_id = ? AND channel_id = ?
    """, (product_id, channel_id))
    result = cursor.fetchone()
    return result[0] if result else None

def delete_product_message(product_id, channel_id):
    cursor.execute("""
    DELETE FROM product_messages 
    WHERE product_id = ? AND channel_id = ?
    """, (product_id, channel_id))
    conn.commit()

def get_all_product_messages():
    cursor.execute("""
    SELECT pm.product_id, pm.channel_id, pm.message_id, tc.channel_username
    FROM product_messages pm
    JOIN telegram_channels tc ON pm.channel_id = tc.channel_id
    """)
    return cursor.fetchall()