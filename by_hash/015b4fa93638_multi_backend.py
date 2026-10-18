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
        
        response = requests.post(f"{host}/api/generate", json=payload, timeout=240)
        response.raise_for_status()
        return response.json().get('response', '')
    
    def _call_mistral_cli(self, prompt: str, system: Optional[str]) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        check = subprocess.run(['which', 'mistral'], capture_output=True)
        if check.returncode != 0:
            raise Exception("mistral CLI not found")
        
        result = subprocess.run(['mistral', 'chat'], input=full_prompt.encode(), 
                              capture_output=True, timeout=240)
        
        if result.returncode != 0:
            raise Exception(f"mistral error: {result.stderr.decode()}")
        
        return result.stdout.decode().strip()
    
    def _call_gemini_cli(self, prompt: str, system: Optional[str]) -> str:
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        
        check = subprocess.run(['which', 'gemini'], capture_output=True)
        if check.returncode != 0:
            raise Exception("gemini not found")
        
        result = subprocess.run(['gemini', full_prompt], capture_output=True, timeout=240)
        
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
