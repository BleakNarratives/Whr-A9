# MOLT - Android/Termux Quick Start

## Step 1: Extract to your project path

```bash
cd /storage/ED7B-AD5A/root_2026/YOU-ARE-HERE/Unfinished-Projects/MoltBleak/openclaw
# Extract molt.zip here
unzip molt.zip
cd molt
```

## Step 2: Install dependencies

```bash
pip install requests
# or
pip install -r requirements.txt
```

## Step 3: Make sure Ollama is running

```bash
# In another Termux session
ollama serve

# Verify it's working
curl http://127.0.0.1:11434/api/tags
```

## Step 4: Test the connection

```bash
python test_connection.py
```

Should see:
```
✅ Ollama connected!
✅ Model works!
🌱 All tests passed! Ready to grow.
```

## Step 5: Run your first molt

```bash
python molt.py "write a function to reverse a string"
```

You should see the tree grow with each iteration!

## Troubleshooting

**"Can't connect to Ollama"**
- Make sure ollama is running: `ollama serve`
- Check the port: `ss -tulpn | grep 11434`

**"Model not found"**
```bash
ollama list  # See what models you have
# Update config.json with your model name
```

**Storage issues?**
- Use smaller models (1.5b instead of 3.5b)
- Clear old memory: `rm memory/improvements.json`
- Set up swap on SD card

## Next Steps

Once it works:
1. Try different tasks
2. Adjust iterations in config.json
3. Experiment with prompts/system.txt
4. Build Code City integration!

---

Remember: This is v1. It's basic but it WORKS. We'll bolt on the cool stuff (Code City, Obelisk, etc) once the core is solid.

**The goal**: Prove that local, recursive improvement beats single-shot cloud APIs.
