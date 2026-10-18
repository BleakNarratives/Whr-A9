#!/usr/bin/env python3
"""
REAPER v3 - The Lodge Edition
Agentic Code Harvester & Executor with Idempotency (Memory)
No Larping Protocol Active.
"""

import re
import subprocess
import sys
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple

class Reaper:
    # Instructional vs Executable Markers
    INSTRUCTION_MARKERS = ['example', 'for instance', 'like this', 'you could', 'template', 'placeholder', 'concept']
    EXECUTABLE_MARKERS = ['run this', 'execute', 'paste this', 'save as', 'deploy', 'test this', 'now do']
    
    # Safety Check
    DANGER_PATTERNS = [r'rm\s+-rf\s+/', r'dd\s+if=', r'mkfs\.', r'curl.*\|\s*sh']

    def __init__(self, conversation_file: str, auto_mode: bool = False, dry_run: bool = False):
        self.conversation_file = Path(conversation_file)
        self.auto_mode = auto_mode
        self.dry_run = dry_run
        self.history_file = Path('~/.reaper_history').expanduser()
        self.code_blocks = []
        self.stats = {'total': 0, 'executable': 0, 'executed': 0, 'skipped': 0, 'failed': 0}
        
        if not self.history_file.exists():
            self.history_file.touch()

    def _get_hash(self, code: str) -> str:
        return hashlib.sha256(code.encode()).hexdigest()

    def _is_duplicate(self, code_hash: str) -> bool:
        return code_hash in self.history_file.read_text()

    def _mark_executed(self, code_hash: str):
        with open(self.history_file, 'a') as f:
            f.write(f"{code_hash}\n")

    def harvest(self):
        print(f"🔪 REAPER v3: Harvesting {self.conversation_file.name}...")
        content = self.conversation_file.read_text()
        full_pattern = r'(.*?)```(\w+)?\n(.*?)```'
        matches = re.findall(full_pattern, content, re.DOTALL)

        for context, lang, code in matches:
            lang = (lang or 'unknown').lower()
            code = code.strip()
            code_hash = self._get_hash(code)
            
            # Smart Classification
            ctx_low = context[-200:].lower() if context else ""
            is_exec = sum(1 for m in self.EXECUTABLE_MARKERS if m in ctx_low)
            is_inst = sum(1 for m in self.INSTRUCTION_MARKERS if m in ctx_low)
            
            classification = 'executable' if is_exec >= is_inst else 'instructional'
            if any(p in code.lower() for p in ['placeholder', 'your_']): classification = 'instructional'

            self.code_blocks.append({
                'lang': lang, 'code': code, 'hash': code_hash,
                'class': classification, 'danger': 'high' if any(re.search(p, code) for p in self.DANGER_PATTERNS) else 'low'
            })
            self.stats['total'] += 1
            if classification == 'executable': self.stats['executable'] += 1

    def execute(self):
        for i, block in enumerate(self.code_blocks, 1):
            if block['class'] != 'executable' or block['lang'] not in ['bash', 'python']:
                continue
            
            if self._is_duplicate(block['hash']):
                print(f"⏭️  Block {i} already in The Lodge. Skipping.")
                self.stats['skipped'] += 1
                continue

            print(f"\n--- Block {i} [{block['lang'].upper()}] ---")
            if not self.auto_mode:
                if input("Execute? (y/n): ").lower() != 'y': continue

            success = False
            if block['lang'] == 'bash':
                res = subprocess.run(block['code'], shell=True, capture_output=True, text=True)
                success = res.returncode == 0
                print(res.stdout or res.stderr)
            elif block['lang'] == 'python':
                with open('temp_r.py', 'w') as f: f.write(block['code'])
                res = subprocess.run(['python3', 'temp_r.py'], capture_output=True, text=True)
                success = res.returncode == 0
                print(res.stdout or res.stderr)
                Path('temp_r.py').unlink()

            if success:
                self._mark_executed(block['hash'])
                self.stats['executed'] += 1
            else:
                self.stats['failed'] += 1

def main():
    print(r"""
    .______       _______      ___      .______    _______ .______      ____   ____ ____ 
    |   _  \     |   ____|    /   \     |   _  \  |   ____||   _  \     \   \ /   /|___ \ 
    |  |_)  |    |  |__      /  ^  \    |  |_)  | |  |__   |  |_)  |     \   V   /   __) |
    |      /     |   __|    /  /_\  \   |   ___/  |   __|  |      /       \     /   |__ < 
    |  |\  \----.|  |____  /  _____  \  |  |      |  |____ |  |\  \----.   \   /    ___) |
    | _| `._____||_______|/__/     \__\ | _|      |_______|| _| `._____|    \_/    |____/ 
                                                                                          
    >> No Larping Protocol: ACTIVE | The Lodge Memory: CONNECTED
    """)
    if len(sys.argv) < 2: return print("Usage: reaper.py <file>")
    r = Reaper(sys.argv[1])
    r.harvest()
    r.execute()

if __name__ == "__main__": main()
