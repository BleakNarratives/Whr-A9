#!/usr/bin/env python3
"""
Quick test script for molt
"""

import sys
from core.ollama_bridge import OllamaClient

def test_ollama():
    print("Testing Ollama connection...")
    client = OllamaClient()
    
    if not client.test_connection():
        print("❌ Can't connect to Ollama at http://127.0.0.1:11434")
        print("Make sure Ollama is running: ollama serve")
        sys.exit(1)
    
    print("✅ Ollama connected!")
    
    print("\nTesting model...")
    response = client.generate("Say 'molt works!' and nothing else", temperature=0.1)
    print(f"Response: {response[:100]}")
    
    if response:
        print("✅ Model works!")
    else:
        print("❌ Model didn't respond")
        sys.exit(1)
    
    print("\n🌱 All tests passed! Ready to grow.")

if __name__ == '__main__':
    test_ollama()
