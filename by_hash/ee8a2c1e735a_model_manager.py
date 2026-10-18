"""
[DNA_TAG]
ORIGIN: Moto4_A9
PILLAR: valet_concierge
PATH: model_manager.py
LAST_SYNC: 2026-08-02T01:12:53Z
[/DNA_TAG]
"""
#!/usr/bin/env python3
"""
model_manager.py – Unified model manager with auto‑detection of vault keys.
No dependency on vertical_ai – reads .env and vault keys from common locations.
"""
import os
import sys
import json
import time
import requests
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path

# ---------- Auto‑detect ROOTBASE ----------
def find_rootbase():
    """Find the RootBase directory by checking common locations."""
    candidates = [
        os.environ.get("ROOTBASE"),
        "/storage/emulated/0/RootBase",
        "/storage/ED7B-AD5A/root_2026",   # your other path
        str(Path.home() / "RootBase"),
        str(Path.home() / "root_2026"),
    ]
    for cand in candidates:
        if cand and Path(cand).exists():
            return cand
    # fallback: current directory
    return os.getcwd()

ROOTBASE = find_rootbase()
print(f"[ModelManager] ROOTBASE set to: {ROOTBASE}")

# ---------- Load keys from .env and vault ----------
def load_env_and_vault():
    """Load .env files and vault keys into os.environ."""
    # 1. Load .env from ROOTBASE and current dir
    for env_file in [".env", f"{ROOTBASE}/.env", f"{ROOTBASE}/vault/.env", f"{ROOTBASE}/.vault/.env"]:
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        if not os.environ.get(k.strip()):
                            os.environ[k.strip()] = v.strip()
    
    # 2. Load vault keys (search multiple directories)
    vault_dirs = [
        Path(ROOTBASE) / "vault" / "keys",
        Path(ROOTBASE) / ".vault" / "keys",
        Path(ROOTBASE) / "keys",
        Path(ROOTBASE) / ".keys",
    ]
    found = False
    for vault_dir in vault_dirs:
        if vault_dir.exists():
            for key_file in vault_dir.glob("*.key"):
                var_name = key_file.stem.upper()
                if not os.environ.get(var_name):
                    with open(key_file) as f:
                        os.environ[var_name] = f.read().strip()
                        found = True
            if found:
                print(f"[ModelManager] Loaded keys from {vault_dir}")
                break
    if not found:
        print("[ModelManager] No vault keys found in common locations.")

# Call it immediately
load_env_and_vault()

# ---------- Model Manager ----------
class ModelManager:
    def __init__(self, cache_dir: str = "./cache"):
        self.providers = {}
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self._load_providers()

    def _load_providers(self):
        # Gemini
        gemini_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_KEY")
        if gemini_key:
            self.providers["gemini"] = {
                "call": self._call_gemini,
                "model": os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
                "key": gemini_key
            }
        # Groq
        groq_key = os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_KEY")
        if groq_key:
            self.providers["groq"] = {
                "call": self._call_groq,
                "model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                "key": groq_key
            }
        # OpenRouter
        or_key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENROUTER_KEY")
        if or_key:
            self.providers["openrouter"] = {
                "call": self._call_openrouter,
                "model": os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"),
                "key": or_key
            }
        # Claude
        claude_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("CLAUDE_API_KEY")
        if claude_key:
            try:
                import anthropic
                self.providers["claude"] = {
                    "call": self._call_claude,
                    "model": os.environ.get("CLAUDE_MODEL", "claude-3-5-sonnet-20240620"),
                    "key": claude_key
                }
            except ImportError:
                print("[ModelManager] anthropic not installed, Claude disabled")
        # OpenAI
        openai_key = os.environ.get("OPENAI_API_KEY")
        if openai_key:
            try:
                import openai
                self.providers["openai"] = {
                    "call": self._call_openai,
                    "model": os.environ.get("OPENAI_MODEL", "gpt-4o"),
                    "key": openai_key
                }
            except ImportError:
                print("[ModelManager] openai not installed, OpenAI disabled")
        # Copilot (gh cli)
        if self._copilot_available():
            self.providers["copilot"] = {
                "call": self._call_copilot,
                "model": "copilot-cli",
                "key": None
            }

        if not self.providers:
            print("[ModelManager] No providers loaded. Check your API keys.")
            print("[ModelManager] Available environment keys:")
            for k in os.environ:
                if "KEY" in k or "API" in k:
                    print(f"  {k} = {os.environ[k][:4]}...")

    # ---------- Call methods (unchanged) ----------
    def _call_gemini(self, provider, prompt, system=None, **kwargs):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{provider['model']}:generateContent?key={provider['key']}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if system:
            payload["system_instruction"] = {"parts": [{"text": system}]}
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]

    def _call_groq(self, provider, prompt, system=None, **kwargs):
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"}
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        payload = {"model": provider["model"], "messages": messages, "max_tokens": kwargs.get("max_tokens", 2000), "temperature": kwargs.get("temperature", 0.7)}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _call_openrouter(self, provider, prompt, system=None, **kwargs):
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {provider['key']}", "Content-Type": "application/json"}
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        payload = {"model": provider["model"], "messages": messages, "max_tokens": kwargs.get("max_tokens", 2000), "temperature": kwargs.get("temperature", 0.7)}
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    def _call_claude(self, provider, prompt, system=None, **kwargs):
        import anthropic
        client = anthropic.Anthropic(api_key=provider["key"])
        messages = [{"role": "user", "content": prompt}]
        response = client.messages.create(
            model=provider["model"],
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7),
            system=system,
            messages=messages
        )
        return response.content[0].text

    def _call_openai(self, provider, prompt, system=None, **kwargs):
        import openai
        client = openai.OpenAI(api_key=provider["key"])
        messages = [{"role": "system", "content": system}] if system else []
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=provider["model"],
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 2000),
            temperature=kwargs.get("temperature", 0.7)
        )
        return response.choices[0].message.content

    def _copilot_available(self):
        import subprocess
        try:
            subprocess.run(["gh", "copilot", "--version"], capture_output=True, check=True)
            return True
        except:
            return False

    def _call_copilot(self, provider, prompt, system=None, **kwargs):
        import subprocess
        cmd = ["gh", "copilot", "suggest", "-t", "general", "-p", prompt]
        if system:
            cmd += ["--context", system]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"Copilot error: {result.stderr}")
        lines = result.stdout.splitlines()
        for line in reversed(lines):
            if "Suggestion:" in line or "Answer:" in line:
                return line.split(":", 1)[-1].strip()
        return result.stdout.strip()

    # ---------- Public API ----------
    def generate(self, provider: str, prompt: str, system: Optional[str] = None, **kwargs) -> str:
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(self.providers.keys())}")
        
        cache_key = f"{provider}_{hash(prompt)}_{hash(system or '')}_{str(kwargs)}"
        cache_path = os.path.join(self.cache_dir, cache_key + ".txt")
        if os.path.exists(cache_path):
            with open(cache_path, "r") as f:
                return f.read()

        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = self.providers[provider]["call"](self.providers[provider], prompt, system, **kwargs)
                with open(cache_path, "w") as f:
                    f.write(result)
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                print(f"[ModelManager] {provider} failed (attempt {attempt+1}): {e}. Retrying...")
                time.sleep(2 ** attempt)
        raise RuntimeError(f"All retries failed for {provider}")

    def list_providers(self) -> List[str]:
        return list(self.providers.keys())

    def health(self) -> Dict[str, bool]:
        status = {}
        for name in self.providers:
            try:
                self.generate(name, "Say OK", max_tokens=5, temperature=0)
                status[name] = True
            except:
                status[name] = False
        return status
