#!/usr/bin/env python3
"""Transcript Watcher - Monitors BasicNote for TERMINAL TRANSCRIPT entries"""

import time
import os
import re
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class TranscriptWatcher:
    def __init__(self, notes_dir: str, molt_dir: str):
        self.notes_dir = Path(notes_dir)
        self.molt_dir = Path(molt_dir)
        self.processed_file = self.molt_dir / 'logs' / 'processed_transcripts.txt'
        self.processed = self._load_processed()
        self.queue = []
        self.max_concurrent = 1
        
    def _load_processed(self) -> set:
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()
    
    def _mark_processed(self, transcript_id: str):
        self.processed.add(transcript_id)
        with open(self.processed_file, 'a') as f:
            f.write(f"{transcript_id}\n")
    
    def watch(self, interval: int = 10):
        print(f"👀 Watching {self.notes_dir} for TERMINAL TRANSCRIPTS...")
        
        while True:
            try:
                self._scan_for_transcripts()
                self._process_queue()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\n🛑 Watcher stopped")
                break
            except Exception as e:
                print(f"⚠️  Error: {e}")
                time.sleep(interval * 2)
    
    def _scan_for_transcripts(self):
        if not self.notes_dir.exists():
            return
        
        for note_file in self.notes_dir.glob("*.txt"):
            file_id = note_file.stem
            
            if file_id in self.processed:
                continue
            
            content = note_file.read_text(errors='ignore')
            
            if "TERMINAL TRANSCRIPT" in content or "FINAL GROWTH:" in content:
                transcript = self._parse_transcript(content, file_id)
                if transcript:
                    self.queue.append(transcript)
                    self._mark_processed(file_id)
                    print(f"📥 Queued: {transcript['title'][:50]}")
    
    def _parse_transcript(self, content: str, file_id: str) -> Optional[Dict]:
        if "FINAL GROWTH:" not in content:
            return None
        
        parts = content.split("FINAL GROWTH:")
        if len(parts) < 2:
            return None
        
        instruction = parts[1].split("📊")[0].strip()
        
        score_match = re.search(r'Final Score:\s*([\d.]+)', content)
        score = float(score_match.group(1)) if score_match else 0.0
        
        seed_match = re.search(r'Seed:\s*(.+?)(?:\n|═)', content)
        seed = seed_match.group(1).strip() if seed_match else "Unknown"
        
        return {
            'id': file_id,
            'timestamp': datetime.now().isoformat(),
            'seed': seed,
            'instruction': instruction,
            'score': score
        }
    
    def _process_queue(self):
        if not self.queue:
            return
        
        transcript = self.queue.pop(0)
        print(f"\n⚙️  Processing: {transcript['seed'][:50]}")
        
        # Execute via molt
        cmd = ['python', str(self.molt_dir / 'molt.py'), transcript['instruction'][:200]]
        
        try:
            subprocess.run(cmd, timeout=300, cwd=str(self.molt_dir))
            self._log(transcript, "Success")
        except Exception as e:
            print(f"❌ Failed: {e}")
            self._log(transcript, f"Error: {e}")
    
    def _log(self, transcript: Dict, result: str):
        log_file = self.molt_dir / 'logs' / 'transcript_log.txt'
        with open(log_file, 'a') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Time: {transcript['timestamp']}\n")
            f.write(f"Seed: {transcript['seed']}\n")
            f.write(f"Result: {result}\n")

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python transcript_watcher.py <notes_directory>")
        sys.exit(1)
    
    notes_dir = sys.argv[1]
    molt_dir = Path(__file__).parent
    
    watcher = TranscriptWatcher(notes_dir, molt_dir)
    watcher.watch()

if __name__ == '__main__':
    main()
