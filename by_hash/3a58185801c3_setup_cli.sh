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
