#!/usr/bin/env python3
"""
AUTHOR: K.M. Talbert / BleakNarratives + Claude (Anthropic)
FILENAME: molt_watchdog.py
PATH: ~/molt_watchdog.py

Molt Watchdog — the wire between arena and real code.

When an agent wins a battle, its skill name maps to a real file
in your codebase. Molt then runs an improvement pass on that file.

The loop:
  1. Watch arena.db for new victories
  2. Find the file that matches the winning skill
  3. Run Molt's improvement engine on it
  4. Save the improved version
  5. Log what changed

This is how the swarm improves YOUR code, not just itself.

Usage:
  python3 ~/molt_watchdog.py              # watch continuously
  python3 ~/molt_watchdog.py --once       # process pending wins once
  python3 ~/molt_watchdog.py --dry-run    # show what would happen
"""

import os
import sys
import json
import time
import sqlite3
import argparse
import urllib.request
from pathlib import Path
from datetime import datetime


ARENA_DB = Path("~/.zeroclaw_genetic/arena.db").expanduser()
WATCHDOG_STATE = Path("~/.molt_watchdog_state.json").expanduser()
OLLAMA_HOST = "http://localhost:11434"
MODEL = "qwen2.5:1.5b"
CODEBASE_ROOTS = [
    Path.home(),
    Path("/storage/ED7B-AD5A/root_2026/Vertical-AI"),
]
LOG_FILE = Path("~/molt_watchdog.log").expanduser()


# ── STATE ─────────────────────────────────────────────────────────────────────

def load_state():
    if WATCHDOG_STATE.exists():
        try:
            return json.loads(WATCHDOG_STATE.read_text())
        except:
            pass
    return {"last_battle_id": 0, "improvements_made": 0, "files_touched": []}


def save_state(state):
    WATCHDOG_STATE.write_text(json.dumps(state, indent=2))


def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


# ── FILE FINDER ───────────────────────────────────────────────────────────────

def find_file_for_skill(skill_name: str) -> str:
    """
    Find the actual file that contains a function matching the skill name.
    Searches codebase roots for a .py file containing 'def skill_name'.
    """
    for root in CODEBASE_ROOTS:
        if not root.exists():
            continue
        for f in root.glob("*.py"):  # Non-recursive — fast
            try:
                content = f.read_text(errors="ignore")
                if f"def {skill_name}" in content:
                    return str(f)
            except:
                pass

    # Deeper search if not found at top level
    for root in [Path.home() / "vertical-ai", Path.home() / "Clawses",
                 Path.home() / "MoltBleak", Path.home() / "zeroclaw_genetic"]:
        if not root.exists():
            continue
        for f in root.rglob("*.py"):
            if "__pycache__" in str(f):
                continue
            try:
                content = f.read_text(errors="ignore")
                if f"def {skill_name}" in content:
                    return str(f)
            except:
                pass

    return None


# ── OLLAMA IMPROVER ───────────────────────────────────────────────────────────

def improve_function(filepath: str, skill_name: str, fitness: float) -> str:
    """
    Ask Ollama to improve the function in the file.
    Returns improved code or None if improvement failed.
    """
    try:
        content = Path(filepath).read_text(errors="ignore")
    except:
        return None

    # Extract just the function
    lines = content.split("\n")
    func_start = None
    func_lines = []

    for i, line in enumerate(lines):
        if f"def {skill_name}" in line:
            func_start = i
        if func_start is not None:
            func_lines.append(line)
            # Stop at next def or end
            if len(func_lines) > 1 and (
                line.startswith("def ") or line.startswith("class ")
            ) and len(func_lines) > 2:
                func_lines = func_lines[:-1]
                break

    if not func_lines:
        return None

    func_code = "\n".join(func_lines[:30])  # Max 30 lines

    prompt = f"""You are a code optimizer. This function was selected by an evolutionary arena with fitness score {fitness:.3f}.
Improve it for: clarity, efficiency, error handling.
Keep the same function signature and behavior.
Return ONLY the improved function code, nothing else.

{func_code}"""

    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3}
    }).encode()

    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result.get("response", "").strip()
    except Exception as e:
        log(f"Ollama error: {e}")
        return None


def apply_improvement(filepath: str, skill_name: str,
                      improved_code: str, dry_run: bool = False) -> bool:
    """
    Replace the original function with the improved version.
    Creates a backup first.
    """
    try:
        original = Path(filepath).read_text(errors="ignore")
    except:
        return False

    # Find function boundaries
    lines = original.split("\n")
    start_idx = None
    end_idx = len(lines)

    for i, line in enumerate(lines):
        if f"def {skill_name}" in line:
            start_idx = i
        elif start_idx is not None and i > start_idx:
            if (line.startswith("def ") or line.startswith("class ")) and not line.startswith(" "):
                end_idx = i
                break

    if start_idx is None:
        return False

    if dry_run:
        log(f"[DRY RUN] Would improve {skill_name} in {filepath}")
        log(f"[DRY RUN] Lines {start_idx}-{end_idx}")
        return True

    # Backup
    backup_path = filepath + f".molt_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    Path(backup_path).write_text(original)

    # Replace
    new_lines = lines[:start_idx] + improved_code.split("\n") + lines[end_idx:]
    Path(filepath).write_text("\n".join(new_lines))

    log(f"✅ Improved {skill_name} in {Path(filepath).name} (backup: {Path(backup_path).name})")
    return True


# ── ARENA WATCHER ─────────────────────────────────────────────────────────────

def get_new_victories(last_battle_id: int):
    """Get battles we haven't processed yet."""
    if not ARENA_DB.exists():
        return []

    with sqlite3.connect(ARENA_DB) as conn:
        rows = conn.execute("""
            SELECT b.id, b.winner_id, b.fitness_delta, a.skills, a.fitness
            FROM battles b
            JOIN agents a ON b.winner_id = a.lineage_id
            WHERE b.id > ? AND a.killswitch_active = 1
            ORDER BY b.id ASC
        """, (last_battle_id,)).fetchall()

    results = []
    for row in rows:
        battle_id, winner_id, delta, skills_json, fitness = row
        try:
            skills = json.loads(skills_json) if skills_json else []
        except:
            skills = []
        results.append({
            "battle_id": battle_id,
            "winner_id": winner_id,
            "delta": delta,
            "skills": skills,
            "fitness": fitness
        })
    return results


def process_victories(victories, dry_run: bool = False) -> int:
    """Process each victory — find the file, improve it."""
    improved = 0

    for v in victories:
        skills = v["skills"]
        if not skills:
            continue

        # Try each skill the winner has
        for skill in skills:
            if not skill or skill.startswith("new_skill_"):
                continue

            filepath = find_file_for_skill(skill)
            if not filepath:
                log(f"[SKIP] No file found for skill: {skill}")
                continue

            log(f"[ARENA→MOLT] Winner {v['winner_id'][:8]} skill '{skill}' → {Path(filepath).name}")

            improved_code = improve_function(filepath, skill, v["fitness"])
            if not improved_code:
                log(f"[SKIP] Ollama couldn't improve {skill}")
                continue

            if apply_improvement(filepath, skill, improved_code, dry_run):
                improved += 1
            break  # One improvement per battle

    return improved


# ── MAIN LOOP ─────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Molt Watchdog — arena → codebase improvement")
    ap.add_argument("--once", action="store_true", help="Process pending, then exit")
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--interval", type=int, default=30, help="Watch interval seconds")
    args = ap.parse_args()

    global MODEL
    MODEL = args.model

    log("=" * 50)
    log("MOLT WATCHDOG — Arena → Codebase")
    log(f"Model: {MODEL} | Dry run: {args.dry_run}")
    log("=" * 50)

    state = load_state()
    log(f"Resuming from battle #{state['last_battle_id']}")
    log(f"Total improvements made: {state['improvements_made']}")

    def run_once():
        victories = get_new_victories(state["last_battle_id"])
        if not victories:
            log("No new victories to process.")
            return

        log(f"Processing {len(victories)} new victories...")
        improved = process_victories(victories, args.dry_run)

        if victories:
            state["last_battle_id"] = victories[-1]["battle_id"]
        state["improvements_made"] += improved
        if not args.dry_run:
            save_state(state)

        log(f"Done. {improved} improvements applied.")

    if args.once:
        run_once()
        return

    log(f"Watching arena every {args.interval}s... Ctrl+C to stop")
    while True:
        try:
            run_once()
            time.sleep(args.interval)
        except KeyboardInterrupt:
            log("Watchdog stopped.")
            break


if __name__ == "__main__":
    main()
