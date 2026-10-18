#!/bin/bash
# Whorl Polyphonic Choir Runner
# Expands linear script execution into concurrent, multi-node verification passes.

PROJECT_ROOT="$HOME/modmind/whorl_choir"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SESSION_LOG="$PROJECT_ROOT/logs/choir_$TIMESTAMP.log"

echo "=== INITIALIZING WHORL HELICAL RUNTIME ===" | tee -a "$SESSION_LOG"

# Define our active choir nodes (simulated concurrent operational threads)
NODES=("syntax_parser" "semantic_vector" "structural_verifier")

echo "[*] Spawning ${#NODES[@]} concurrent runtime nodes..." | tee -a "$SESSION_LOG"

for node in "${NODES[@]}"; do
    NODE_FILE="$PROJECT_ROOT/nodes/${node}.py"
    
    # Generate a dummy worker script for each node if it doesn't exist
    if [ ! -f "$NODE_FILE" ]; then
        echo "import sys, time; print(f'Node [${node}] active at time: {time.time()}')" > "$NODE_FILE"
    fi
    
    echo "[+] Firing node thread: $node" | tee -a "$SESSION_LOG"
    python3 "$NODE_FILE" >> "$SESSION_LOG" 2>&1 &
done

# Wait for background node threads to finish their pass
wait

echo "=== HELICAL PASS COMPLETE. LOG SAVED TO: $SESSION_LOG ===" | tee -a "$SESSION_LOG"
