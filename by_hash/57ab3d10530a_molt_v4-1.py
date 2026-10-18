"""
[DNA_TAG]
ORIGIN: Moto4_A9
PILLAR: valet_concierge
PATH: molt_v4-1.py
LAST_SYNC: 2026-08-02T01:12:54Z
[/DNA_TAG]
"""
#!/usr/bin/env python3
"""
MOLT v4 - The one that actually works.
Key fix over v3: scoring is done by the LLM, not by checking if 'def' exists.
Path: /storage/emulated/0/RootBase/molt_v4.py

Usage:
  python3 molt_v4.py "your task here" --iters 5
  python3 molt_v4.py --file /path/to/code.py --iters 3
  python3 molt_v4.py --self  # molt improves itself. yes really.
"""

import sys
import json
import time
import argparse
import textwrap
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ── CONFIG ────────────────────────────────────────────────────────────────────

OLLAMA_HOST = "http://127.0.0.1:11434"
OLLAMA_MODEL = "qwen2.5:1.5b"
WIDTH = 74

# ── RENDERER (kept the good parts of v3) ─────────────────────────────────────

class Renderer:
    def seed(self, task: str):
        print("\n" + "─" * WIDTH)
        print(f"  🌱 MOLT v4 — SEED TASK:")
        for line in textwrap.wrap(task[:200], width=WIDTH - 5):
            print(f"     {line}")
        print("─" * WIDTH)

    def ring(self, i: int, total: int):
        print(f"\n 🌀 RING {i}/{total}")

    def branch(self, score: float, content: str, is_improvement: bool):
        if score >= 0.80:
            icon, color = "🌟", "\033[1;35m"
        elif score >= 0.65:
            icon, color = "🌿", "\033[1;32m"
        else:
            icon, color = "🍂", "\033[1;33m"

        tag = " ✨ IMPROVEMENT" if is_improvement else ""
        print(f" ┃  {icon}  Score: {color}{score:.2f}\033[0m{tag}")

        # Show a snippet of the output
        snippet = content.strip()[:300].replace("\n", " ")
        for line in textwrap.wrap(snippet, width=WIDTH - 10):
            print(f" ┃    {line}")

    def reasoning(self, text: str):
        """Show why the score was given."""
        print(f" ┃    \033[2m💭 {text[:120]}\033[0m")

    def canopy(self, branches: int, improvements: int, best_score: float):
        print("\n" + "━" * WIDTH)
        print("                    🌳💎🌳\n                    ║║║║║")
        print(f" 📊 {branches} rings | {improvements} improvements | best score: {best_score:.2f}")
        print("━" * WIDTH + "\n")

    def error(self, msg: str):
        print(f" ❌ {msg}")

    def best(self, content: str):
        print(f"\n 🏆 BEST OUTPUT:\n")
        for line in textwrap.wrap(content.strip()[:600], width=WIDTH - 4):
            print(f"    {line}")
        print()


# ── OLLAMA BRIDGE ─────────────────────────────────────────────────────────────

def ask(prompt: str, system: Optional[str] = None,
        max_tokens: int = 1500) -> Tuple[str, bool]:
    """
    Call Ollama. Returns (response_text, success).
    Simple and direct — no class needed for this.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": max_tokens
                }
            },
            timeout=300
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip(), True
    except Exception as e:
        return f"Error: {e}", False


# ── THE ACTUAL BRAIN ──────────────────────────────────────────────────────────

SYSTEM_IMPROVE = """You are MOLT, a recursive code improvement engine.
Your job: take a task and previous attempts, and generate a meaningfully better version.

Rules:
- Actually improve on what came before. Don't repeat the same output.
- Be specific and practical. No filler.
- If the task involves code, return working code.
- If it involves analysis or suggestions, return structured, actionable text.
- Be concise. Quality over length."""

SYSTEM_EVALUATE = """You are a strict technical evaluator for a code improvement engine.
Score the output on a scale from 0.0 to 1.0.

Scoring guide:
  0.9-1.0: Excellent. Specific, actionable, correct, meaningfully better than baseline.
  0.7-0.8: Good. Mostly correct with minor gaps.
  0.5-0.6: Mediocre. Generic, vague, or partially correct.
  0.3-0.4: Poor. Off-topic, incorrect, or unhelpful.
  0.0-0.2: Useless. Empty, broken, or harmful.

Return ONLY a JSON object like this, nothing else:
{"score": 0.75, "reasoning": "one sentence explanation"}"""


def generate_improvement(task: str, previous: List[Dict]) -> str:
    """Generate an improved attempt based on previous results."""
    context = ""
    if previous:
        context = f"\n\nPrevious attempts ({len(previous)}):\n"
        for i, p in enumerate(previous[-2:], 1):  # Last 2 only
            context += f"\nAttempt {i} (score {p['score']:.2f}):\n{p['output'][:400]}...\n"
        context += "\nNow generate a meaningfully better version."
    else:
        context = "\nThis is the first attempt. Do your best."

    prompt = f"Task: {task}{context}"
    output, ok = ask(prompt, system=SYSTEM_IMPROVE, max_tokens=1500)
    return output if ok else ""


def evaluate_output(task: str, output: str,
                    previous_best: Optional[str] = None) -> Tuple[float, str]:
    """
    The fix. LLM evaluates quality instead of checking for 'def'.
    Returns (score, reasoning).
    """
    prev_context = ""
    if previous_best:
        prev_context = f"\n\nPrevious best output for comparison:\n{previous_best[:300]}"

    prompt = f"""Task: {task}

Output to evaluate:
{output[:600]}
{prev_context}

Score this output. Return only JSON."""

    result, ok = ask(prompt, system=SYSTEM_EVALUATE, max_tokens=100)

    if not ok:
        return 0.5, "evaluation failed"

    # Parse the JSON score
    try:
        # Strip any markdown fencing if model wrapped it
        clean = result.strip().strip("```json").strip("```").strip()
        data = json.loads(clean)
        score = float(data.get("score", 0.5))
        reasoning = str(data.get("reasoning", ""))
        # Clamp to valid range
        score = max(0.0, min(1.0, score))
        return score, reasoning
    except Exception:
        # If JSON parse fails, try to extract a number
        import re
        nums = re.findall(r'0\.\d+', result)
        if nums:
            return float(nums[0]), "parsed from malformed response"
        return 0.5, "could not parse evaluation"


# ── MOLT ENGINE ───────────────────────────────────────────────────────────────

class MoltV4:
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.renderer = Renderer() if not headless else None
        self.results: List[Dict] = []
        self.improvements = 0

    def run(self, task: str, max_iterations: int = 5) -> Dict:
        if self.renderer:
            self.renderer.seed(task)

        best_score = 0.0
        best_output = ""

        for i in range(1, max_iterations + 1):
            if self.renderer:
                self.renderer.ring(i, max_iterations)

            # Generate
            output = generate_improvement(task, self.results)
            if not output:
                if self.renderer:
                    self.renderer.error("Backend returned empty response")
                continue

            # Evaluate — the actual fix
            score, reasoning = evaluate_output(
                task, output,
                previous_best=best_output if best_output else None
            )

            is_improvement = score > best_score
            if is_improvement:
                best_score = score
                best_output = output
                self.improvements += 1

            result = {
                "iteration": i,
                "output": output,
                "score": score,
                "reasoning": reasoning,
                "is_improvement": is_improvement
            }
            self.results.append(result)

            if self.renderer:
                self.renderer.branch(score, output, is_improvement)
                if reasoning:
                    self.renderer.reasoning(reasoning)

            # Save improvements to disk
            if is_improvement:
                self._save(task, result)

            time.sleep(0.1)

        if self.renderer:
            self.renderer.canopy(max_iterations, self.improvements, best_score)
            if best_output:
                self.renderer.best(best_output)

        return {
            "output": best_output,
            "score": best_score,
            "improvements": self.improvements,
            "iterations": len(self.results)
        }

    def _save(self, task: str, result: Dict):
        """Save improvements to disk for future reference."""
        try:
            log_dir = Path("/storage/emulated/0/RootBase/molt_v4_log")
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "improvements.jsonl"
            with open(log_file, "a") as f:
                f.write(json.dumps({
                    "task": task[:100],
                    "timestamp": time.time(),
                    "score": result["score"],
                    "reasoning": result["reasoning"],
                    "output_preview": result["output"][:300]
                }) + "\n")
        except Exception:
            pass


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="MOLT v4 — Recursive Improvement Engine")
    parser.add_argument("task", nargs="?", default="",
                        help="Task or objective to improve")
    parser.add_argument("--file", type=str,
                        help="Read task from a source file (analyzes the file)")
    parser.add_argument("--iters", type=int, default=5,
                        help="Number of improvement iterations")
    parser.add_argument("--headless", action="store_true",
                        help="JSON output only, no ASCII")
    parser.add_argument("--self", dest="self_improve", action="store_true",
                        help="Molt improves itself (points at molt_v4.py)")
    parser.add_argument("--model", type=str, default=OLLAMA_MODEL,
                        help=f"Ollama model to use (default: {OLLAMA_MODEL})")
    args = parser.parse_args()

    # Override model if specified
    global OLLAMA_MODEL
    OLLAMA_MODEL = args.model

    # Determine task
    task = args.task

    if args.self_improve:
        own_code = Path(__file__).read_text()[:2000]
        task = f"Improve this code — identify weaknesses and suggest specific enhancements:\n\n{own_code}"
    elif args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {args.file}")
            sys.exit(1)
        code = file_path.read_text(errors="ignore")
        task = f"Analyze and suggest improvements for this code from {file_path.name}:\n\n{code[:3000]}"
    elif not task:
        task = "Review the CodeMentor MVP architecture and suggest the three most impactful improvements."

    headless = args.headless or not sys.stdout.isatty()
    engine = MoltV4(headless=headless)
    result = engine.run(task, max_iterations=args.iters)

    if headless:
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
