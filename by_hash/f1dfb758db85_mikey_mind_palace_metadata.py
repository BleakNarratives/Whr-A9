# mikey_mind_palace_metadata.py
import asyncio
from telethon import TelegramClient
import json
from datetime import datetime

api_id = 33115446
api_hash = 'cb54c1e70834720a8116da5760d0d4ae'

client = TelegramClient('mikey_session', api_id, api_hash)

async def scrape_metadata():
    await client.start()
    print("🔥 Connected. Fetching saved messages (metadata only)...")

    messages = []
    async for msg in client.iter_messages('me', wait_time=0.2):
        if not msg.out:
            continue
        
        entry = {
            'id': msg.id,
            'date': msg.date.isoformat(),
            'text': msg.text,
            'media_type': None,
            'media_size': None,
            'mime_type': None,
        }
        
        if msg.media:
            # Detect type without downloading
            if msg.photo:
                entry['media_type'] = 'photo'
                entry['media_size'] = msg.photo.size if hasattr(msg.photo, 'size') else None
            elif msg.document:
                entry['media_type'] = 'document'
                entry['media_size'] = msg.document.size
                entry['mime_type'] = msg.document.mime_type
                # Check if it's a GIF (mime type video/mp4 or image/gif, or attribute)
                if msg.document.mime_type == 'video/mp4' and any(getattr(a, 'animated', False) for a in msg.document.attributes if hasattr(a, 'animated')):
                    entry['media_type'] = 'gif'
                elif msg.document.mime_type == 'image/gif':
                    entry['media_type'] = 'gif'
            elif msg.video:
                entry['media_type'] = 'video'
                entry['media_size'] = msg.video.size
            elif msg.audio:
                entry['media_type'] = 'audio'
                entry['media_size'] = msg.audio.size
            elif msg.voice:
                entry['media_type'] = 'voice'
        
        messages.append(entry)
        
        if len(messages) % 100 == 0:
            print(f"⏳ {len(messages)} messages processed...")

    with open('saved_messages_metadata.json', 'w') as f:
        json.dump(messages, f, indent=2, default=str)
    
    print(f"\n✅ Complete! {len(messages)} message records saved.")
    # Summary
    media_counts = {}
    for m in messages:
        t = m['media_type'] or 'text'
        media_counts[t] = media_counts.get(t, 0) + 1
    print("📊 Media breakdown:")
    for t, count in media_counts.items():
        print(f"   {t}: {count}")

asyncio.run(scrape_metadata())