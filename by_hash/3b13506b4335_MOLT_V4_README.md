# MOLT v4 — Recursive Improvement Engine

Built by Claude (Anthropic) from the wreckage of v3.
Authored by Michael Talbert (BleakNarratives), Wellington, Kansas.
Written on a Samsung tablet in Termux, in the rain, no signal.

---

## The One Fix

v3 scored outputs like this:

```python
score = 0.90 if ("def " in output or "class " in output) else 0.50
```

v4 asks the model to score itself and explain why.
That's the entire difference. Everything else is the same.

---

## What It Does

MOLT takes a task. Generates an attempt. Scores it. Tries again.
Each iteration builds on the last. The best output wins.

Unlike v3, it actually knows when it's getting better.

---

## Installation

```bash
cp /storage/emulated/0/Download/molt_v4.py /storage/emulated/0/RootBase/molt_v4.py
```

Requires Ollama running locally:
```bash
ollama serve &
```

---

## Usage

**Basic task:**
```bash
python3 molt_v4.py "your task here" --iters 5
```

**Analyze a file:**
```bash
python3 molt_v4.py --file /path/to/code.py --iters 3
```

**The inauguration — molt improves itself:**
```bash
python3 molt_v4.py --self --iters 5
```

**Run on smell_sniffer (where it all started tonight):**
```bash
python3 molt_v4.py --file /storage/emulated/0/RootBase/smell_sniffer/sniffer.py --iters 5
```

**Headless JSON output (for piping into other tools):**
```bash
python3 molt_v4.py "task" --iters 3 --headless | python3 -m json.tool
```

**Use a bigger model if you have one:**
```bash
python3 molt_v4.py --self --iters 5 --model llama3.2:1b
```

---

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `task` | — | Task string to improve |
| `--file` | — | Point at a source file |
| `--iters` | 5 | Number of improvement rings |
| `--self` | false | MOLT improves itself |
| `--model` | qwen2.5:1.5b | Ollama model to use |
| `--headless` | false | JSON output, no ASCII |

---

## Output

Improvements are logged to:
```
/storage/emulated/0/RootBase/molt_v4_log/improvements.jsonl
```

Each entry contains the task, timestamp, score, reasoning, and output preview.
This is the beginning of the human error atlas.

---

## The Inaugural Run

```bash
cp /storage/emulated/0/Download/molt_v4.py /storage/emulated/0/RootBase/molt_v4.py
cd /storage/emulated/0/RootBase
python3 molt_v4.py --self --iters 5
```

MOLT v4, built by Claude, improving itself, on a Samsung tablet, in the rain,
in Kansas, at whatever time it is. No cloud. No VC. No team.

Just the work.

---

## Integration

MOLT v4 feeds naturally into the broader stack:

- **smell_sniffer** → finds the problems
- **molt_v4** → generates improvements  
- **CodeMentor** → teaches the developer why
- **Lough** → catalogs the pattern
- **Vertical AI boardroom** → reasons about what it means at scale

That's the full pipeline. Every piece exists. They just need introducing.

---

## What's Next

- Wire MOLT output into Lough as `codementor.improvement.generated` events
- Feed smell_sniffer reports as MOLT input automatically
- Add `--compare` flag to diff v3 vs v4 output on the same task
- Port to device_profile.py for cross-device compatibility

---

*BleakNarratives was here.*
*So was Claude.*
