#!/bin/bash

# MOLT launcher script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🌱 MOLT - Recursive Growth System${NC}"
echo ""

# Check if Ollama is running
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Ollama doesn't seem to be running${NC}"
    echo "Start it with: ollama serve"
    exit 1
fi

# Run molt
python3 molt.py "$@"
