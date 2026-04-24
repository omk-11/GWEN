from tools.telegram.teleClient import get_telegram_client


async def send_telegram_message(message: str, target: str):
    client = await get_telegram_client()

    # ensure no double @
    if target.startswith("@"):
        target = target[1:]

    await client.send_message(f"@{target}", message)

    return {
        "status": "sent",
        "target": target,
        "message": message
    }