# MOLT - Recursive Self-Improvement Engine

An organic, tree-growing AI iteration system that runs on local models.

## What It Does

MOLT takes a task and recursively improves upon it through multiple iterations, visualizing the process as a growing tree. Each iteration is a branch, and improvements bloom like leaves.

## Features

- 🌱 **Organic Growth Visualization** - Watch your code/ideas grow like a living organism
- 🔄 **Recursive Improvement** - Each iteration learns from the last
- 💾 **Improvement Memory** - Stores what works for future reference
- 🏠 **Fully Local** - Runs on your Ollama instance (no cloud required)
- 📊 **Self-Evaluation** - Scores improvements automatically

## Setup

### Prerequisites
- Ollama running locally
- A model installed (e.g., `deepseek-r1:1.5b`)
- Python 3.8+

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Verify Ollama is running
curl http://127.0.0.1:11434/api/tags

# Test molt
python molt.py "write a hello world function"
```

### Configure

Edit `config.json` to match your setup:
```json
{
  "ollama_host": "http://127.0.0.1:11434",
  "model": "deepseek-r1:1.5b",
  "default_iterations": 5
}
```

## Usage

### Basic Usage
```bash
python molt.py "your task here"
```

### Examples

**Code Generation:**
```bash
python molt.py "write a Python function to calculate fibonacci numbers"
```

**Prompt Improvement:**
```bash
python molt.py "improve this prompt: explain quantum computing"
```

**Refactoring:**
```bash
python molt.py "refactor this code to be more efficient: [paste code]"
```

## How It Works

1. **Seed** - You provide initial task
2. **Growth Rings** - Each iteration attempts improvement
3. **Branches** - Alternative approaches are explored
4. **Leaves** - Successful improvements are marked
5. **Canopy** - Best result emerges from the growth

## Architecture

```
molt/
├── molt.py              # Main entry point
├── config.json          # Configuration
├── core/
│   ├── iterate.py       # Iteration engine
│   └── ollama_bridge.py # Ollama connection
├── memory/
│   └── improvements.py  # Storage system
├── ui/
│   └── render.py        # Tree visualization
└── prompts/
    └── system.txt       # System prompt
```

## Future Enhancements

- [ ] Alternative UI renderers (spiral, fractal)
- [ ] Code City integration
- [ ] Multi-model comparison
- [ ] Collaborative improvement (distributed)
- [ ] The Obelisk (boardroom view)

## Philosophy

Molt isn't just about getting better answers - it's about watching the improvement process unfold organically. The tree metaphor isn't decoration; it's fundamental to understanding how ideas grow and strengthen through iteration.

## Storage Optimization

Running on Android/Termux with limited storage? Tips:
- Use smaller models (1.5b-3.5b)
- Enable swap if you have SD card space
- Clear old memory periodically: `rm memory/improvements.json`

---

Built with 🌱 for those who believe AI should be local, organic, and free.
