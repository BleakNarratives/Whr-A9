# mikey_mind_palace_excavator.py
import asyncio
from telethon import TelegramClient
import json
import os
from datetime import datetime

api_id = 33115446
api_hash = 'cb54c1e70834720a8116da5760d0d4ae'

client = TelegramClient('mikey_session', api_id, api_hash)
MEDIA_DIR = 'telegram_media'

async def scrape_all():
    await client.start()
    print("🔥 Connected. Drilling through subfloor...")

    os.makedirs(MEDIA_DIR, exist_ok=True)
    
    messages = []
    async for msg in client.iter_messages('me', wait_time=0.5):  # be gentle to API
        if not msg.out:
            continue  # only messages you sent (saved ones)
        
        # Basic metadata
        entry = {
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': msg.text,
            'has_media': msg.media is not None,
            'file': None,
        }
        
        # If there's media, download it
        if msg.media:
            try:
                path = await msg.download_media(file=MEDIA_DIR)
                entry['file'] = path
                print(f"📥 Downloaded: {path}")
            except Exception as e:
                entry['file'] = f"FAILED: {e}"
        
        messages.append(entry)
        
        # Progress indicator
        if len(messages) % 50 == 0:
            print(f"⏳ {len(messages)} messages processed...")

    # Save JSON
    with open('saved_messages_full.json', 'w') as f:
        json.dump(messages, f, indent=2, default=str)
    
    print(f"\n✅ Complete! {len(messages)} messages saved.")
    print(f"📁 Media saved in '{MEDIA_DIR}'")

asyncio.run(scrape_all())