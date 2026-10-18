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

print("🧶 Testing The Loom...")
from plugins.loom_graph import LoomGraph, seed_loom
loom = seed_loom()
loom.weave("claude", "DEFEATED", "test_bot", {"derby": "smoke"})
neighborhood = loom.get_fiber_neighborhood("claude", depth=1)
print(f"  ✅ Loom woven — {len(loom.G.nodes)} nodes, {len(loom.G.edges)} fibers")

print("\n" + "─" * 40)
print("✅ ALL SYSTEMS NOMINAL")
print("   JANUS + JaneBox + Trap Registry + Derby + Amusement Park")
print("   Five layers. One ship. No survivors.")
print("─" * 40)

print("🌀 Testing Whorl Translator...")
from plugins.whorl_translator import WhorlTranslator, seed_whorl_translator
wt = seed_whorl_translator()
print(f"  ✅ Whorl live — {len(wt.runtime.agents)} agents at tick {wt.runtime.tick}")

# Test Three.js scene generation
scene = wt.to_threejs_scene()
print(f"  ✅ Three.js scene — {len(scene['objects'])} objects")

# Test strand emission
python_code = wt.emit_to_strand('python')
print(f"  ✅ Python strand emitted — {len(python_code)} chars")

# Test loom integration
wt.weave_into_loom()
loom_nodes = len(wt.loom.G.nodes) if hasattr(wt.loom.G, 'nodes') else len(wt.loom.G["nodes"])
print(f"  ✅ Whorl woven into Loom — {loom_nodes} total nodes")

print("🎲 Testing Quantum Derby...")
from plugins.quantum_derby import QuantumDerby
qd = QuantumDerby(jb, derby)
tasks = derby.list_tasks()
contest = qd.create_contest(tasks[0]["task_id"], "regional", 5)
qd.submit_entry(contest["contest_id"], "claude", "test", "def x(): pass", 10, 0.7)
qd.submit_entry(contest["contest_id"], "gemini", "test", "def x(): return 1", 15, 0.65)
odds = qd.calculate_odds(contest["contest_id"])
print(f"  ✅ Odds calculated: {len(odds)} agents")
qd.place_wager(contest["contest_id"], "claude", "gemini", "reputation", 10)
result = qd.collapse_contest(contest["contest_id"])
winner = result["final_scores"][0]["agent_id"] if result["final_scores"] else "none"
print(f"  ✅ Contest collapsed — winner: {winner}")
print("🔍 Testing Lookinglass Bridge...")
from plugins.lookinglass_bridge import LookinglassBridge
lb = LookinglassBridge()
result = lb.full_pipeline("plugins/janebox.py", 30)
print(f"  ✅ Lookinglass resolved: {result.get('status', 'unknown')}")
print("⚔️ Testing The Gauntlet...")
from plugins.gauntlet import Gauntlet, seed_gauntlet
g = seed_gauntlet()
courses = g.list_courses()
print(f"  ✅ Gauntlet active — {len(courses)} courses")
if courses:
    course = courses[0]
    result = g.attempt_obstacle(
        course["course_id"], 0, "claude",
        "def current_timestamp():\n    import time\n    return int(time.time())",
        30
    )
    if "score" in result:
        print(f"  ✅ First obstacle: {result['status']} — score: {result['score']}")
    else:
        print(f"  ⚠️ First obstacle: {result.get('status', '?')} — {result.get('reason', result.get('status', 'unknown'))}")
    if result.get("next_unlocked"):
        print(f"  ✅ Next unlocked: {result['next_unlocked']}")


print("🌓 Testing The Pantheon...")
from plugins.pantheon import Pantheon, seed_pantheon, DEITIES
p = seed_pantheon()
rankings = p.get_pantheon_rankings()
print(f"  ✅ Pantheon active — {len(rankings)} entities, {len(DEITIES)} deities")
mirror = p.duality_mirror("user_demo")
print(f"  ✅ Duality Mirror: past={mirror['past']['total_favor']:.1f} favor, can_pass={mirror['past']['can_pass_janus']}")
feast = p.pantheonic_feast()
print(f"  ✅ Pantheonic Feast: {feast['total_rituals_performed']} rituals, crown={feast['crown_holder'] or 'none'}")
