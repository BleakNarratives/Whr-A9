"""
Ollama Bridge - Connect to local DeepSeek model
"""

import requests
import json
from typing import Dict, Optional

class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", model: str = "deepseek-r1:1.5b"):
        self.host = host.rstrip('/')
        self.model = model
        self.api_url = f"{self.host}/api/generate"
        
    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        """Generate response from Ollama"""
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048
            }
        }
        
        if system:
            payload["system"] = system
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            result = response.json()
            return result.get('response', '')
            
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama at {self.host}. Is it running?") from e
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get('models', [])
            return any(self.model in m.get('name', '') for m in models)
        except:
            return False
