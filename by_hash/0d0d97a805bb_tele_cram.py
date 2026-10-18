import asyncio
from telethon import TelegramClient
import json

api_id = 33115446
api_hash = 'cb54c1e70834720a8116da5760d0d4ae'

client = TelegramClient('mikey_session', api_id, api_hash)

async def scrape_saved():
    await client.start()
    print("✅ Connected. Fetching saved messages...")
    
    saved = []
    async for msg in client.iter_messages('me', reverse=False):
        if msg.out:  # messages you sent
            saved.append({
                'id': msg.id,
                'date': msg.date.isoformat(),
                'text': msg.text,
                'file': msg.file and msg.file.name
            })
    
    with open('saved_messages.json', 'w') as f:
        json.dump(saved, f, indent=2, default=str)
    
    print(f"✅ Saved {len(saved)} messages to saved_messages.json")

asyncio.run(scrape_saved())