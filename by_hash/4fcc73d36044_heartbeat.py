#!/usr/bin/env python3
"""
HEARTBEAT — poor man's cron for Termux
Runs scheduled jobs without crond
"""
import time
import subprocess
from datetime import datetime

JOBS = [
    {
        "name": "janitor_resurface",
        "interval_seconds": 3600,
        "cmd": ["python3", 
                "/data/data/com.termux/files/home/RootBase/Janus/core/JANUS.py",
                "--resurface"]
    }
]

def run_job(job):
    print(f"[{datetime.now().isoformat()}] Running: {job['name']}")
    try:
        subprocess.run(job["cmd"], timeout=30)
    except Exception as e:
        print(f"  ✗ {job['name']} failed: {e}")

def main():
    print("💓 HEARTBEAT online")
    timers = {job["name"]: 0 for job in JOBS}
    
    while True:
        now = time.time()
        for job in JOBS:
            if now - timers[job["name"]] >= job["interval_seconds"]:
                run_job(job)
                timers[job["name"]] = now
        time.sleep(60)

if __name__ == "__main__":
    main()
