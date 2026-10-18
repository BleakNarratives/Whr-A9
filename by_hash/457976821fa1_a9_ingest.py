import os
import sys
import time
import json

TARGET_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
TOMBSTONE_LOG = os.path.expanduser("~/modmind/whorl_choir/logs/tombstones.jsonl")

os.makedirs(os.path.dirname(TOMBSTONE_LOG), exist_ok=True)

print(f"[*] A9 Ingest Node active on target: {TARGET_DIR}")

def log_tombstone(filepath, reason):
    record = {
        "timestamp": time.time(),
        "file": filepath,
        "status": "TOMBSTONED",
        "reason": reason
    }
    with open(TOMBSTONE_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")
    print(f"[X] TOMBSTONE: {filepath} -> {reason}")

# Scan directory for dead/deprecated markers or empty scripts
for root, dirs, files in os.walk(TARGET_DIR):
    for file in files:
        filepath = os.path.join(root, file)
        # Example condition: flag empty files or deprecated extensions as tombstones
        if os.path.getsize(filepath) == 0:
            log_tombstone(filepath, "Zero-byte footprint / dead weight")
        elif ".bak" in file or "~" in file:
            log_tombstone(filepath, "Legacy backup file / non-active branch")

print("[*] Ingestion pass and tombstone logging complete.")
