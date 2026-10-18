# mikey_palace_full.py
import asyncio
from telethon import TelegramClient
import json

api_id = 33115446
api_hash = 'cb54c1e70834720a8116da5760d0d4ae'

client = TelegramClient('mikey_session', api_id, api_hash)

async def get_all_saved():
    await client.start()
    print("🔥 Connected. Fetching ALL saved messages...")

    messages = []
    count = 0
    async for msg in client.iter_messages('me', wait_time=0.5):
        if not msg.out:
            continue
        messages.append({
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': msg.text,
            'media_type': 'document' if msg.document else ('photo' if msg.photo else None),
            'size': msg.document.size if msg.document else None
        })
        count += 1
        if count % 100 == 0:
            print(f"⏳ {count} messages so far...")
    with open('all_saved_messages.json', 'w') as f:
        json.dump(messages, f, indent=2, default=str)
    print(f"\n✅ Total: {count} messages saved.")

asyncio.run(get_all_saved())