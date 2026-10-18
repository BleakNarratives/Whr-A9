"""
Ollama Bridge - Connect to local DeepSeek model
"""

import requests
import json
from typing import Dict, Optional, Tuple

class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", model: str = "deepseek-r1:1.5b"):
        self.host = host.rstrip('/')
        self.model = model
        self.api_generate_url = f"{self.host}/api/generate"
        self.api_tags_url = f"{self.host}/api/tags" # Added for test_connection

    def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> Tuple[Optional[str], Optional[str]]:
        """Generate response from Ollama. Returns (response_text, error_message)."""
        
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
                self.api_generate_url,
                json=payload,
                timeout=240
            )
            response.raise_for_status() # Raises HTTPError for bad responses (4xx or 5xx)
            result = response.json()
            return result.get('response', ''), None # Return response and no error
            
        except requests.exceptions.ConnectionError as e:
            return None, f"ConnectionError: Unable to connect to Ollama at {self.host}. Is Ollama running (`ollama serve`)?"
        except requests.exceptions.Timeout as e:
            return None, f"Timeout: Ollama did not respond within 240 seconds. {e}"
        except requests.exceptions.HTTPError as e:
            return None, f"HTTPError: Ollama API returned status {response.status_code}. Details: {e}"
        except json.JSONDecodeError as e:
            return None, f"JSONError: Ollama response was not valid JSON. Details: {e}"
        except requests.exceptions.RequestException as e:
            return None, f"RequestError: An unexpected error occurred during request to Ollama: {e}"
        except Exception as e:
            return None, f"UnexpectedError: An unhandled error occurred: {e}"

    def test_connection(self) -> Tuple[bool, str]:
        """Test if Ollama is running and model is available. Returns (is_connected, message)."""
        try:
            # Test connectivity to the /api/tags endpoint
            response = requests.get(self.api_tags_url, timeout=5)
            response.raise_for_status() # Will raise HTTPError for 4xx/5xx responses
            
            # Check if the model is in the list of available models
            models = response.json().get('models', [])
            if any(self.model in m.get('name', '') for m in models):
                return True, "Ollama is connected and model is available."
            else:
                available_models = ", ".join([m.get('name', 'unknown') for m in models])
                return False, f"Model '{self.model}' not found. Available models: {available_models}. Please 'ollama pull {self.model}'."
                
        except requests.exceptions.ConnectionError:
            return False, f"ConnectionError: Unable to connect to Ollama at {self.host}. Is Ollama running (`ollama serve`)?"
        except requests.exceptions.Timeout:
            return False, f"Timeout: Ollama did not respond within 5 seconds during connection test. Check network or Ollama server."
        except requests.exceptions.HTTPError as e:
            return False, f"HTTPError: Ollama API ({self.api_tags_url}) returned status {response.status_code}. Details: {e}"
        except json.JSONDecodeError as e:
            return False, f"JSONError: Ollama /api/tags response was not valid JSON. Details: {e}. Raw response: {response.text[:200]}..."
        except requests.exceptions.RequestException as e:
            return False, f"RequestError: An unexpected error occurred during connection test: {e}"
        except Exception as e:
            return False, f"UnexpectedError: An unhandled error occurred during connection test: {e}"
