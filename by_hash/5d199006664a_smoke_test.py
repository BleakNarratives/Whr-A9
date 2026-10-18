#!/usr/bin/env python3
import sys, os, time
sys.path.insert(0, os.path.expanduser("~/RootBase/Janus"))

run_id = f"smoke_{int(time.time())}"

print("🌓 Testing JANUS core...")
from core.JANUS import deposit_sediment, read_sediment, pack_baton, catch_baton, sweep_option, resurface_option
print("  ✅ JANUS imports clean")

print("📦 Testing JaneBox...")
from plugins.janebox import JaneBox
print("  ✅ JaneBox imports clean")

print("🔌 Testing Supabase connection...")
jb = JaneBox()
print("  ✅ JaneBox initialized")

print(f"✍️  Testing write ({run_id})...")
jb.write(whorl_key=run_id, payload={"test": True, "origin": "smoke_test"}, agent_id="claude", session_id="smoke_session")
print("  ✅ Write succeeded")

print("📖 Testing read...")
data = jb.read(run_id)
print(f"  ✅ Read succeeded → {data['payload']}")

print("🤝 Testing hand_off...")
jb.hand_off("claude", "gemini-cli", run_id)
print("  ✅ Hand off succeeded")

print("🗑️  Testing soft delete...")
jb.delete(run_id)
print("  ✅ Soft delete succeeded")

print("🧱 Testing sediment...")
trail = read_sediment(last_n=5)
print(f"  ✅ Sediment readable — {len(trail)} entries")

print("🔐 Testing Trap Registry...")
from plugins.trap_registry import TrapRegistry, seed_default_challenges
tr = seed_default_challenges()
session = tr.start_session("claude")
challenge = tr.get_challenge("scribe")
result = tr.attempt_challenge(session["session_id"], challenge["challenge_id"], {"modules": ["core/JANUS.py", "plugins/janebox.py", "plugins/trap_registry.py"]})
print(f"  ✅ Scribe: {result['status']}")
bad_session = tr.start_session("test_bot")
bad_result = tr.attempt_challenge(bad_session["session_id"], challenge["challenge_id"], {"modules": ["core/JANUS.py", "database.py", "api.py"]})
print(f"  ✅ Bad proof: {bad_result['status']}")

print("🏟️  Testing EOF Derby...")
from plugins.derby import Derby, seed_derby_tasks
derby = seed_derby_tasks()
tasks = derby.list_tasks()
print(f"  ✅ Derby live — {len(tasks)} tasks ready")
entry = derby.submit_entry(
    tasks[0]["task_id"], "claude", "smoke_session",
    "from core.JANUS import read_sediment\ndef get_last_agent():\n    trail = read_sediment(3)\n    return trail[0]['agent_id'] if trail else None",
    45
)
print(f"  ✅ Entry scored: {entry['total']:.2f}")
lb = derby.get_leaderboard()
print(f"  ✅ Leaderboard: {len(lb['rankings'])} ranked")

print("🎪 Testing Amusement Park...")
from plugins.amusement_park import AmusementPark, seed_park_rides
park = seed_park_rides()
summary = park.get_park_summary()
print(f"  ✅ Park open — {summary['total_rides']} rides, {summary['approved']} approved")
rot = park.ride_of_the_day()
print(f"  {rot}")

print("\n" + "─" * 40)
print("✅ ALL SYSTEMS NOMINAL")
print("   JANUS + JaneBox + Trap Registry + Derby + Amusement Park")
print("   Five layers. One ship. No survivors.")
print("─" * 40)
