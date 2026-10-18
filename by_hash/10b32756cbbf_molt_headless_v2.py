#!/usr/bin/env python3
"""
MOLT_HEADLESS - Standalone Background Worker
Path: /data/data/com.termux/files/home/MoltBleak/molt_headless.py
"""

import sys
import json
import argparse
from pathlib import Path

# Fix pathing for Termux environment
BASE_DIR = Path(__file__).parent
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

try:
    # We import the logic, but we don't trigger the UI
    from molt import Molt
except ImportError as e:
    print(json.dumps({"error": f"Import failed: {e}"}))
    sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Molt Headless Engine")
    parser.add_argument('--task', type=str, required=True, help='Task for the AI')
    parser.add_argument('--iters', type=int, default=3, help='Number of recursive loops')
    args = parser.parse_args()

    try:
        engine = Molt()
        # We pass headless=True to the run method we discussed
        # This ensures no TreeRenderer or 8-bit ASCII interrupts the JSON pipe
        result = engine.run(args.task, max_iterations=args.iters)
        
        # Output ONLY JSON for the Vibe CLI to consume
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    main()
