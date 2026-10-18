#!/bin/bash
# MOLT v2 Installer - Creates all files in current directory

set -e

echo "🌱 Installing MOLT v2..."

# Create directory structure
mkdir -p core memory ui/themes logs prompts/templates

echo "📁 Creating core/multi_backend.py..."
cat > core/multi_backend.py << 'EOFILE'
"""
Multi-Backend Orchestrator
Coordinates Ollama, Mistral CLI, and Gemini CLI
Falls back when one fails
"""

import subprocess
import json
import time
from typing import Optional, Dict, List
import requests

class MultiBackend:
    def __init__(self, config: Dict):
        self.config = config
        self.backends = ['ollama', 'mistral', 'gemini']
        self.failure_counts = {b: 0 for b in self.backends}
        self.last_success = None
        
    def generate(self, prompt: str, system: Optional[str] = None, max_retries: int = 3) -> str:
        """Try backends in order until one works"""
        
        # Start with last successful backend
        if self.last_success:
            backends = [self.last_success] + [b for b in self.backends if b != self.last_success]
        else:
            backends = self.backends
        
        for backend in backends:
            for attempt in range(max_retries):
                try:
                    result = self._call_backend(backend, prompt, system)
                    if result and len(result) > 10:
                        self.last_success = backend
                        self.failure_counts[backend] = 0
                        return result
                except Exception as e:
                    print(f"[{backend}] Attempt {attempt + 1} failed: {e}")
                    time.sleep(2 ** attempt)
            
            self.failure_counts[backend] += 1
        
        return "Error: All backends failed"
    
    def _call_backend(self, backend: str, prompt: str, system: Optional[str]) -> str:
        if backend == 'ollama':
            return self._call_ollama(prompt, system)
        elif backend == 'mistral':
            return self._call_mistral_cli(prompt, system)
        elif backend == 'gemini':
            return self._call_gemini_cli(prompt, system)
        raise ValueError(f"Unknown backend: {backend}")
    
    def _call_ollama(self, prompt: str, system: Optional[str]) -> str:
        host = self.config.get('ollama_host', 'http://127.0.0.1:11434')
        model = self.config.get('ollama_model', 'deepseek-r1:1.5b')
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1024}
        }
        
        if system:
            payload["system"] = system
        
        response = requests.post(f"{host}/api/generate", json=payload, timeout=180)
        response.raise_for_status()
        return response.json().get('response', '')
    
    def _call_mistral_cli(self, prompt: str, system: Optional[str]) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        check = subprocess.run(['which', 'mistral'], capture_output=True)
        if check.returncode != 0:
            raise Exception("mistral CLI not found")
        
        result = subprocess.run(['mistral', 'chat'], input=full_prompt.encode(), 
                              capture_output=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"mistral error: {result.stderr.decode()}")
        
        return result.stdout.decode().strip()
    
    def _call_gemini_cli(self, prompt: str, system: Optional[str]) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        check = subprocess.run(['which', 'gemini'], capture_output=True)
        if check.returncode != 0:
            raise Exception("gemini not found")
        
        result = subprocess.run(['gemini', full_prompt], capture_output=True, timeout=120)
        
        if result.returncode != 0:
            raise Exception(f"gemini error: {result.stderr.decode()}")
        
        return result.stdout.decode().strip()
    
    def health_check(self) -> Dict[str, bool]:
        health = {}
        for backend in self.backends:
            try:
                result = self._call_backend(backend, "say OK", None)
                health[backend] = bool(result and len(result) > 0)
            except:
                health[backend] = False
        return health
    
    def get_best_backend(self) -> str:
        return min(self.failure_counts, key=self.failure_counts.get)
EOFILE

echo "📁 Creating transcript_watcher.py..."
cat > transcript_watcher.py << 'EOFILE'
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
EOFILE

echo "📁 Updating config.json..."
cat > config.json << 'EOFILE'
{
  "use_multi_backend": true,
  "ollama_host": "http://127.0.0.1:11434",
  "ollama_model": "deepseek-r1:1.5b",
  "mistral_enabled": true,
  "gemini_enabled": true,
  "default_iterations": 5,
  "temperature": 0.7,
  "ui_theme": "tree",
  "log_level": "INFO"
}
EOFILE

echo "📁 Creating setup_cli.sh..."
cat > setup_cli.sh << 'EOFILE'
#!/bin/bash
echo "🔧 Checking CLI tools..."

command -v mistral &> /dev/null && echo "✅ Mistral CLI found" || echo "⚠️  Mistral CLI not found"
command -v gemini &> /dev/null && echo "✅ Gemini CLI found" || echo "⚠️  Gemini CLI not found"
curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1 && echo "✅ Ollama running" || echo "⚠️  Ollama not responding"

echo ""
echo "Testing backends..."
python3 << 'EOF'
from core.multi_backend import MultiBackend
import json

with open('config.json') as f:
    config = json.load(f)

backend = MultiBackend(config)
health = backend.health_check()

print("\nBackend Health:")
for name, status in health.items():
    icon = "✅" if status else "❌"
    print(f"  {icon} {name}")
EOF
EOFILE

chmod +x setup_cli.sh
chmod +x transcript_watcher.py

echo ""
echo "✅ MOLT v2 installed!"
echo ""
echo "Next steps:"
echo "  1. ./setup_cli.sh          # Check what's working"
echo "  2. python molt.py 'test'   # Try it out"
echo "  3. python transcript_watcher.py ~/path/to/notes  # Start watcher"
