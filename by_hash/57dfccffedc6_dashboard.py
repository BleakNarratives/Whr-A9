#!/usr/bin/env python3
"""JANUS Live Dashboard — 3D Whorl, Quantum Odds, Pivot/Ring input."""

import sys, os, json, time, threading
sys.path.insert(0, os.path.expanduser("~/RootBase/Janus"))

from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit
from core.janus_system import JanusSystem
from plugins.derby import Derby
from plugins.amusement_park import AmusementPark
from plugins.loom_graph import LoomGraph
from plugins.whorl_translator import WhorlTranslator, seed_whorl_translator
from plugins.quantum_derby import QuantumDerby
from plugins.lookinglass_bridge import LookinglassBridge

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

system = JanusSystem(auto_seed=True)
whorl = seed_whorl_translator()
qderby = QuantumDerby(system.jb, system.derby)
lookinglass = LookinglassBridge(system.loom, whorl)

# Start a demo contest if none active
active_odds = qderby.get_active_odds()
if not active_odds:
    tasks = system.derby.list_tasks()
    if tasks:
        qderby.create_contest(tasks[0]["task_id"], layer="regional", duration_minutes=60)
        qderby.submit_entry(qderby._get_contests()["active_contests"][0]["contest_id"], "claude", "demo_session", "def solution(): pass", 20)
        print("🎲 Demo contest created")

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>JANUS Live — Quantum Derby + Whorl 3D + Pivot/Ring</title>
<style>
:root { --bg: #0a0a0f; --panel: #111118; --accent: #00ff88; --warn: #ffaa00; --danger: #ff4444; --text: #ccc; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Courier New',monospace; background:var(--bg); color:var(--text); overflow:hidden; height:100vh; }
.dashboard { display:grid; grid-template-columns:1fr 1fr 1fr; grid-template-rows:auto 1fr 1fr; gap:10px; padding:10px; height:100vh; }
.panel { background:var(--panel); border-radius:8px; padding:15px; border:1px solid #222; overflow-y:auto; }
.header { grid-column:1/-1; display:flex; justify-content:space-between; align-items:center; background:#000; border-bottom:2px solid var(--accent); }
.header h1 { color:var(--accent); font-size:1.5em; }
.status-dot { width:12px; height:12px; border-radius:50%; display:inline-block; margin-right:10px; }
.nominal { background:var(--accent); box-shadow:0 0 10px var(--accent); }
.degraded { background:var(--warn); box-shadow:0 0 10px var(--warn); }
.agent-list li { padding:5px; margin:5px 0; background:#1a1a22; border-radius:4px; display:flex; justify-content:space-between; }
.rank-badge { color:var(--accent); font-weight:bold; }
.ride-card { background:#1a1a22; padding:8px; margin:5px 0; border-radius:4px; border-left:3px solid var(--accent); }
.metric { display:flex; justify-content:space-between; padding:4px 0; border-bottom:1px solid #222; }
.metric-value { color:var(--accent); }
#whorlCanvas { width:100%; height:200px; border-radius:8px; }
#oddsPanel { font-size:0.9em; }
#ringMenu { position:fixed; top:50%; left:50%; transform:translate(-50%,-50%); width:200px; height:200px; background:rgba(0,0,0,0.8); border-radius:50%; display:none; z-index:1000; }
.ring-item { position:absolute; color:var(--accent); font-size:0.8em; }
#pivotIndicator { position:fixed; bottom:20px; left:20px; width:80px; height:80px; background:rgba(0,255,136,0.1); border:2px solid var(--accent); border-radius:50%; display:none; }
#pivotDot { position:absolute; width:10px; height:10px; background:var(--accent); border-radius:50%; top:50%; left:50%; transform:translate(-50%,-50%); }
.nav-hint { position:fixed; bottom:20px; left:50%; transform:translateX(-50%); background:#1a1a22; padding:8px 20px; border-radius:20px; font-size:0.8em; color:#666; }
</style>
</head>
<body>
<div class="dashboard">
  <div class="panel header">
    <h1>🌓 JANUS LIVE</h1>
    <div><span id="sysStatus"><span class="status-dot nominal"></span>ALL SYSTEMS NOMINAL</span></div>
    <div id="timestamp" style="font-size:0.8em"></div>
  </div>
  <div class="panel">
    <h3>🏆 Leaderboard</h3>
    <ul class="agent-list" id="leaderboard"></ul>
  </div>
  <div class="panel">
    <h3>🌀 Whorl 3D</h3>
    <canvas id="whorlCanvas"></canvas>
  </div>
  <div class="panel">
    <h3>🎲 Quantum Odds</h3>
    <div id="oddsPanel"></div>
  </div>
  <div class="panel">
    <h3>🎡 Amusement Park</h3>
    <div id="rides"></div>
  </div>
  <div class="panel">
    <h3>📊 System Metrics</h3>
    <div id="metrics"></div>
  </div>
  <div class="panel">
    <h3>📡 Live Events</h3>
    <div id="events" style="font-size:0.85em"></div>
  </div>
</div>
<div id="ringMenu"></div>
<div id="pivotIndicator"><div id="pivotDot"></div></div>
<div class="nav-hint" id="navHint">🕹️ Pivot ready | 💍 Ring: clap to summon | 📱 3D Whorl active</div>

<script src="https://cdn.socket.io/4.5.0/socket.io.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1644/hands.min.js"></script>
<script>
const socket = io();

// ── Three.js Whorl Viewer ────────────────────
let scene, camera, renderer, whorlObjects = [];
function initThreeJS() {
  const canvas = document.getElementById('whorlCanvas');
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a0f);
  camera = new THREE.PerspectiveCamera(60, canvas.clientWidth/canvas.clientHeight, 0.1, 10);
  camera.position.set(1.5, 1.5, 3);
  camera.lookAt(0,0,0);
  renderer = new THREE.WebGLRenderer({canvas, antialias:true});
  renderer.setSize(canvas.clientWidth, canvas.clientHeight);
  const light = new THREE.AmbientLight(0x404066);
  scene.add(light);
  const pointLight = new THREE.PointLight(0xffaa00, 1, 5);
  pointLight.position.set(0,2,2);
  scene.add(pointLight);
  animate();
}
function animate() {
  requestAnimationFrame(animate);
  whorlObjects.forEach(obj => {
    if(obj.userData.rotationSpeed) obj.rotation.y += obj.userData.rotationSpeed * 0.01;
  });
  renderer.render(scene, camera);
}
function updateWhorlScene(sceneData) {
  whorlObjects.forEach(o => scene.remove(o));
  whorlObjects = [];
  sceneData.objects.forEach(obj => {
    const geo = new THREE.SphereGeometry(obj.radius, 16, 16);
    const mat = new THREE.MeshPhongMaterial({color: obj.color, opacity: obj.opacity, transparent: true});
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(obj.position[0], obj.position[1], obj.position[2]);
    mesh.userData = {rotationSpeed: obj.rotation_speed || 0};
    scene.add(mesh);
    whorlObjects.push(mesh);
  });
}
window.addEventListener('resize', () => {
  if(renderer) {
    const canvas = document.getElementById('whorlCanvas');
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    camera.aspect = canvas.clientWidth/canvas.clientHeight;
    camera.updateProjectionMatrix();
  }
});
initThreeJS();

// ── Socket Events ────────────────────────────
socket.on('connect', () => console.log('🟢 Connected'));
socket.on('system_update', (data) => {
  updateDashboard(data);
  if(data.whorlScene) updateWhorlScene(data.whorlScene);
});
socket.on('live_event', (ev) => {
  const eventsDiv = document.getElementById('events');
  eventsDiv.innerHTML = `<div class="ride-card pulse">⚡ ${ev.timestamp}: ${ev.action} by ${ev.agent}</div>` + eventsDiv.innerHTML;
});
socket.on('odds_update', (odds) => {
  const panel = document.getElementById('oddsPanel');
  panel.innerHTML = odds.map(c => 
    `<div><b>Contest ${c.contest_id}</b><br>` +
    c.odds.map(o => `  ${o.agent_id}: ${(o.win_probability*100).toFixed(1)}%`).join('<br>') + '</div>'
  ).join('<hr>');
});

function updateDashboard(data) {
  // Leaderboard
  const lb = document.getElementById('leaderboard');
  lb.innerHTML = (data.leaderboard||[]).map(r =>
    `<li><span class="rank-badge">#${r.rank}</span> ${r.agent_id} <span class="score">${r.average?.toFixed(2)||r.best_score?.toFixed(2)}</span></li>`
  ).join('');
  // Rides
  const rides = document.getElementById('rides');
  rides.innerHTML = (data.rides||[]).slice(0,3).map(r => `<div class="ride-card">🎢 ${r.name} <span style="float:right">${r.score?.toFixed(2)}</span></div>`).join('') + `<div style="color:var(--accent)">${data.rideOfDay||''}</div>`;
  // Metrics
  const metrics = document.getElementById('metrics');
  metrics.innerHTML = `
    <div class="metric"><span>JaneBox</span><span class="metric-value">${data.janeBox||'...'}</span></div>
    <div class="metric"><span>Loom Nodes</span><span class="metric-value">${data.loom||0}</span></div>
    <div class="metric"><span>Whorl Agents</span><span class="metric-value">${data.whorl?.agent_count||0}</span></div>
  `;
  document.getElementById('timestamp').textContent = data.timestamp||'';
}

// ── Ring (Clap Detection) ────────────────────
navigator.mediaDevices?.getUserMedia({audio:true}).then(stream => {
  const audioCtx = new AudioContext();
  const source = audioCtx.createMediaStreamSource(stream);
  const analyser = audioCtx.createAnalyser();
  source.connect(analyser);
  analyser.fftSize = 256;
  const buffer = new Uint8Array(analyser.frequencyBinCount);
  let lastClap = 0;
  setInterval(() => {
    analyser.getByteFrequencyData(buffer);
    const avg = buffer.reduce((a,b)=>a+b)/buffer.length;
    if(avg > 50 && Date.now() - lastClap > 1000) {
      lastClap = Date.now();
      toggleRingMenu();
      socket.emit('ring_event', {type:'clap', timestamp: new Date().toISOString()});
    }
  }, 100);
}).catch(() => console.log('🎤 Mic optional'));

function toggleRingMenu() {
  const menu = document.getElementById('ringMenu');
  if(menu.style.display === 'block') { menu.style.display = 'none'; return; }
  menu.innerHTML = '<div class="ring-item" style="top:20px;left:50%;transform:translateX(-50%)">Leaderboard</div>'+
    '<div class="ring-item" style="bottom:20px;left:50%;transform:translateX(-50%)">Whorl View</div>'+
    '<div class="ring-item" style="left:20px;top:50%;transform:translateY(-50%)">Odds</div>'+
    '<div class="ring-item" style="right:20px;top:50%;transform:translateY(-50%)">Events</div>';
  menu.style.display = 'block';
  setTimeout(() => menu.style.display = 'none', 3000);
}

// ── Pivot (MediaPipe Hands) ──────────────────
let pivotActive = false;
async function initPivot() {
  const video = document.createElement('video');
  video.style.display = 'none';
  document.body.appendChild(video);
  const stream = await navigator.mediaDevices.getUserMedia({video:true});
  video.srcObject = stream;
  await video.play();
  const Hands = new Hands({locateFile: file => `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4.1644/${file}`});
  Hands.setOptions({maxNumHands:1, modelComplexity:0, minDetectionConfidence:0.7, minTrackingConfidence:0.5});
  Hands.onResults(results => {
    if(results.multiHandLandmarks?.length > 0) {
      pivotActive = true;
      document.getElementById('pivotIndicator').style.display = 'block';
      const lm = results.multiHandLandmarks[0];
      const thumb = lm[4]; // thumb tip
      const dot = document.getElementById('pivotDot');
      dot.style.left = (50 + (thumb.x - 0.5)*80) + '%';
      dot.style.top = (50 + (thumb.y - 0.5)*80) + '%';
      socket.emit('pivot_event', {x: thumb.x, y: thumb.y, timestamp: new Date().toISOString()});
    } else {
      pivotActive = false;
      document.getElementById('pivotIndicator').style.display = 'none';
    }
  });
  setInterval(() => { Hands.send({image: video}); }, 100);
}
navigator.mediaDevices?.getUserMedia({video:true}).then(() => initPivot()).catch(() => console.log('📷 Camera optional for Pivot'));
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('connect')
def handle_connect():
    emit_data = build_dashboard_data()
    emit('system_update', emit_data)
    emit('odds_update', qderby.get_active_odds())

@socketio.on('ring_event')
def handle_ring(data):
    emit('live_event', {'action':'RING_SUMMONED','agent':'user','timestamp':data['timestamp']}, broadcast=True)

@socketio.on('pivot_event')
def handle_pivot(data):
    # Pivot data can steer dashboard panels in future
    pass


@socketio.on('lookinglass_resolve')
def handle_lookinglass(data):
    file_path = data.get('file', '')
    line_number = data.get('line', 1)
    depth = data.get('depth', 2)
    result = lookinglass.full_pipeline(file_path, line_number, depth)
    emit('lookinglass_scene', result, broadcast=True)


def build_dashboard_data():
    report = system.system_report()
    lb = system.derby.get_leaderboard()
    park = system.park.get_park_summary()
    whorl_snapshot = whorl.get_state_snapshot()
    loom_nodes = len(system.loom.G.nodes) if hasattr(system.loom.G,'nodes') else len(system.loom.G["nodes"])
    return {
        "timestamp": report["timestamp"],
        "leaderboard": lb.get("rankings",[]),
        "rides": park.get("top_rides",[]),
        "rideOfDay": report["rideOfDay"],
        "janeBox": report["janeBox"],
        "loom": loom_nodes,
        "whorl": {"agent_count": len(whorl_snapshot["agents"]), "tick": whorl_snapshot["tick"]},
        "whorlScene": whorl.to_threejs_scene(),
        "allSystemsNominal": True
    }

def emit_updates():
    while True:
        socketio.sleep(5)
        socketio.emit('system_update', build_dashboard_data())
        socketio.emit('odds_update', qderby.get_active_odds())

if __name__ == '__main__':
    socketio.start_background_task(emit_updates)
    print("🌓 JANUS Dashboard + Whorl 3D + Quantum Odds + Pivot/Ring on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
