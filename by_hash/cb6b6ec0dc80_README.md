# Mikey Mind Palace 🏰

> A living, breathing map of my digital soul—built with OpenClaw, boardroom personas, and a city that never sleeps.

## What This Is

The Mikey Mind Palace is an **autonomous digital twin** of everything I've saved, said, and thought across Telegram (and eventually beyond). It's not just a backup—it's a **visual, explorable city** where each message becomes a building, each conversation a district, and each file a landmark.

It's powered by:
- **OpenClaw (Moltbot)** – The always-on agent that connects to Telegram and executes tasks.
- **Boardroom Personas** – A council of AI minds (Architect, Adversary, Analyst, CMO) that organize, critique, and narrate the data.
- **Code City** – A 16‑bit, retro-future visualization that turns chaos into skyline.
- **The Dark Archive** – An encrypted, IPFS-backed vault for the things that shouldn't be public (but must be kept).

## Why It Matters

Because I've spent years dumping my brain into Telegram. Because the starvation lane taught me that nothing lasts unless you *build* it. Because if I can map my own mind, I can help others map theirs—and that changes everything.

## Architecture Overview

```

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Telegram      │────▶│   OpenClaw      │────▶│   Raw JSON      │
│   (Saved Msgs)  │     │   (Scraper)     │     │   + Media       │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
│
▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Boardroom     │◀────│   Swarm         │────▶│   Processed     │
│   Personas      │     │   (Classifiers) │     │   Data (JSON)   │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
│
▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Code City     │◀────│   City Builder  │────▶│   Live Map      │
│   (Visualizer)  │     │   (Python)      │     │   (HTML/JS)     │
└─────────────────┘     └─────────────────┘     └─────────────────┘

```

## Setup

### Prerequisites
- Python 3.8+
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org/apps))
- OpenClaw (optional but recommended) – [molt.bot](https://molt.bot)
- IPFS (for Dark Archive) – `pkg install ipfs` or download from [ipfs.tech](https://ipfs.tech)

### Installation

1. Clone this repo:
   ```bash
   git clone https://github.com/yourhandle/mikey-mind-palace.git
   cd mikey-mind-palace
```

1. Install Python dependencies:
   ```bash
   pip install telethon
   ```
2. Run the Telegram excavator:
   ```python
   python mikey_mind_palace_excavator.py
   ```
   (You'll be prompted for your phone number and verification code.)
3. Wait. This may take hours depending on your history. Go make tea.
4. Once complete, you'll have:
   · saved_messages_full.json – all your saved messages with metadata.
   · telegram_media/ – all downloaded files (images, docs, etc.).

Next Steps (Optional but Awesome)

1. Swarm Classification

Run the swarm classifiers to cluster your messages:

```bash
python swarm_classify.py --input saved_messages_full.json --output clustered.json
```

2. Boardroom Personas

Feed the clustered data to the boardroom for strategic insights:

```bash
python boardroom_personas.py --data clustered.json --output city_plan.json
```

3. Code City Visualization

Generate a 16‑bit city from the city plan:

```bash
python code_city_builder.py --plan city_plan.json --output docs/
```

Then open docs/index.html in your browser.

4. Dark Archive (IPFS)

Pin everything to IPFS for permanent, decentralized storage:

```bash
ipfs add -r telegram_media saved_messages_full.json
```

Save the hash – that's your data's forever address.

The Vision

This is Phase 1. Phase 2 connects more services (Signal, WhatsApp, email). Phase 3 makes the city interactive—you'll be able to click a building and read the message, zoom into districts, watch the city evolve in real time as new data flows in.

Phase 4? You decide. It's your mind palace.

Credits

Built by Mikey, with a lot of late nights and a little help from DeepSeek, the boardroom, and the swarm.

License

MIT – because sharing is caring, and I want everyone to build their own city.