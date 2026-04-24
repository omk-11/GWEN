import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv("APIIDTELE", "0"))
api_hash = os.getenv("APIHASHTELE")
SESSION_FILE = "tools/telegram/session.txt"

client = None


async def get_telegram_client():
    global client

    if client:
        return client

    # load session if exists
    session_str = ""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            session_str = f.read().strip()

    client = TelegramClient(
        StringSession(session_str),
        api_id,
        api_hash
    )

    await client.connect()

    # 🔥 CRITICAL FIX
    if not await client.is_user_authorized():
        print("🔐 Login required")

        phone = input("Enter phone number (with +91): ")
        await client.send_code_request(phone)

        code = input("Enter OTP: ")
        await client.sign_in(phone, code)

        # save session
        with open(SESSION_FILE, "w") as f:
            f.write(client.session.save())

        print("✅ Session saved successfully!")

    return client

async def shutdown_telegram():
    global client

    if client:
        await client.disconnect()
        client = None