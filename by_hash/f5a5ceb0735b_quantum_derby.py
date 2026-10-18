#!/usr/bin/env python3
"""Quantum Derby — PEQ scoring, wagers, observer collapse, fog-of-war, Bayesian odds."""

import os, sys, json, hashlib, time, math, random
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, os.path.expanduser("~/RootBase/Janus"))

from core.JANUS import deposit_sediment
from plugins.janebox import JaneBox
from plugins.derby import Derby

# ── Free entropy sources ────────────────────────────

def fetch_moon_illumination():
    try:
        import urllib.request
        ts = int(time.time())
        url = f"https://api.farmsense.net/v1/moonphases/?d={ts}"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            return float(data[0]["Illumination"]) / 100.0
    except:
        return random.random()

def fetch_blockchain_height():
    try:
        import urllib.request
        with urllib.request.urlopen("https://blockchain.info/q/getblockcount", timeout=5) as resp:
            return int(resp.read().strip())
    except:
        return int(time.time()) % 100000

def fetch_atmospheric_noise():
    try:
        import urllib.request
        url = "https://www.random.org/integers/?num=1&min=0&max=255&col=1&base=10&format=plain&rnd=new"
        with urllib.request.urlopen(url, timeout=5) as resp:
            return int(resp.read().strip()) / 255.0
    except:
        return random.random()

# ── Quantum Derby ───────────────────────────────────

class QuantumDerby:
    WAGER_TYPES = ["reputation", "priority", "trap_skip", "ride_sponsorship", "vanity_wave"]

    def __init__(self, janebox=None, derby=None):
        self.jb = janebox or JaneBox()
        self.derby = derby or Derby(self.jb)
        self.contests_key = "quantum_derby_contests"
        self._init_contests()

    def _init_contests(self):
        if not self.jb.read(self.contests_key):
            self.jb.write(self.contests_key, {"active_contests": [], "closed_contests": []}, "quantum_derby", "system")

    def _get_contests(self):
        data = self.jb.read(self.contests_key)
        return data["payload"] if data else {"active_contests": [], "closed_contests": []}

    def _save_contests(self, contests):
        self.jb.write(self.contests_key, contests, "quantum_derby", "system")

    def create_contest(self, task_id, layer="regional", duration_minutes=10, creator="system"):
        contests = self._get_contests()
        contest_id = hashlib.sha256(f"{task_id}{time.time()}".encode()).hexdigest()[:12]
        contest = {
            "contest_id": contest_id,
            "task_id": task_id,
            "layer": layer,
            "creator": creator,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "closes_at": (datetime.now(timezone.utc) + timedelta(minutes=duration_minutes)).isoformat(),
            "submissions": [],
            "wagers": [],
            "observer_seed": None,
            "collapsed": False,
            "final_scores": []
        }
        contests["active_contests"].append(contest)
        self._save_contests(contests)
        deposit_sediment("quantum_derby", "CREATE_CONTEST", contest_id, "active", {"layer": layer})
        return contest

    def submit_entry(self, contest_id, agent_id, session_id, solution_code, token_count, projected_score=None):
        contests = self._get_contests()
        contest = next((c for c in contests["active_contests"] if c["contest_id"] == contest_id), None)
        if not contest:
            return {"status": "rejected", "reason": "Contest not found or closed"}
        entry = {
            "entry_id": hashlib.sha256(f"{contest_id}{agent_id}{time.time()}".encode()).hexdigest()[:12],
            "agent_id": agent_id,
            "session_id": session_id,
            "solution_code": solution_code,
            "token_count": token_count,
            "projected_score": projected_score or self._project_score(agent_id, token_count),
            "submitted_at": datetime.now(timezone.utc).isoformat()
        }
        contest["submissions"].append(entry)
        self._save_contests(contests)
        deposit_sediment(agent_id, "QUANTUM_SUBMIT", contest_id, "submitted", {"projected": entry["projected_score"]})
        return {"status": "submitted", "entry_id": entry["entry_id"]}

    def place_wager(self, contest_id, from_agent, to_agent, wager_type, stake=10):
        contests = self._get_contests()
        contest = next((c for c in contests["active_contests"] if c["contest_id"] == contest_id), None)
        if not contest:
            return {"status": "rejected", "reason": "Contest not active"}
        if wager_type not in self.WAGER_TYPES:
            return {"status": "rejected", "reason": f"Unknown wager type: {wager_type}"}
        wager = {
            "from": from_agent,
            "to": to_agent,
            "type": wager_type,
            "stake": stake,
            "placed_at": datetime.now(timezone.utc).isoformat()
        }
        contest["wagers"].append(wager)
        self._save_contests(contests)
        return {"status": "placed", "wager": wager}

    def collapse_contest(self, contest_id):
        contests = self._get_contests()
        contest = next((c for c in contests["active_contests"] if c["contest_id"] == contest_id), None)
        if not contest:
            return {"status": "rejected", "reason": "Contest not active"}
        # Generate observer seed from entropy sources
        moon = fetch_moon_illumination()
        btc_height = fetch_blockchain_height()
        noise = fetch_atmospheric_noise()
        combined = f"{moon}:{btc_height}:{noise}:{time.time()}"
        seed = hashlib.sha256(combined.encode()).hexdigest()
        contest["observer_seed"] = seed
        random.seed(seed)

        # Score all submissions with observer collapse multiplier
        final_scores = []
        for sub in contest["submissions"]:
            base_score = sub["projected_score"]
            observer_multiplier = 0.8 + random.random() * 0.4  # 0.8–1.2
            final = base_score * observer_multiplier
            final_scores.append({
                "entry_id": sub["entry_id"],
                "agent_id": sub["agent_id"],
                "projected": base_score,
                "observer_multiplier": round(observer_multiplier, 3),
                "final_score": round(final, 4)
            })
        final_scores.sort(key=lambda x: x["final_score"], reverse=True)
        for i, s in enumerate(final_scores):
            s["rank"] = i + 1

        contest["final_scores"] = final_scores
        contest["collapsed"] = True
        contests["active_contests"] = [c for c in contests["active_contests"] if c["contest_id"] != contest_id]
        contests["closed_contests"].append(contest)
        self._save_contests(contests)
        deposit_sediment("observer", "COLLAPSE", contest_id, "collapsed", {"winner": final_scores[0]["agent_id"] if final_scores else "none"})
        return {"status": "collapsed", "final_scores": final_scores}

    def _project_score(self, agent_id, token_count):
        """Project a score based on historical derby performance and token efficiency."""
        lb = self.derby.get_leaderboard()
        agent_stats = next((r for r in lb["rankings"] if r["agent_id"] == agent_id), None)
        if agent_stats:
            base = agent_stats["average"]
        else:
            base = 0.5
        efficiency = max(0, 1.0 - token_count / 4000)
        return round(base * 0.7 + efficiency * 0.3, 3)

    def calculate_odds(self, contest_id):
        """Bayesian odds for each agent in a contest."""
        contests = self._get_contests()
        contest = next((c for c in contests["active_contests"] + contests["closed_contests"] if c["contest_id"] == contest_id), None)
        if not contest or not contest["submissions"]:
            return []
        submissions = contest["submissions"]
        total_weight = sum(s["projected_score"] for s in submissions)
        odds = []
        for s in submissions:
            prob = s["projected_score"] / total_weight if total_weight > 0 else 0
            odds.append({
                "agent_id": s["agent_id"],
                "projected": s["projected_score"],
                "win_probability": round(prob, 3)
            })
        odds.sort(key=lambda x: x["win_probability"], reverse=True)
        return odds

    def get_active_odds(self):
        """Live odds for all active contests."""
        contests = self._get_contests()
        all_odds = []
        for c in contests["active_contests"]:
            odds = self.calculate_odds(c["contest_id"])
            all_odds.append({"contest_id": c["contest_id"], "task_id": c["task_id"], "odds": odds})
        return all_odds
