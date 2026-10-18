>>> FILE: dupefinder.py
#!/data/data/com.termux/files/usr/bin/python3
import os
import hashlib
from pathlib import Path
from collections import defaultdict

def hash_file(path):
    hasher = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            hasher.update(chunk)
    return hasher.hexdigest()

def scan_for_dupes(dirs):
    size_map = defaultdict(list)
    # Group by size first (fast)
    for base in dirs:
        p = Path(base).expanduser()
        if not p.exists():
            continue
        for f in p.rglob('*'):
            if f.is_file():
                try:
                    sz = f.stat().st_size
                    size_map[sz].append(f)
                except:
                    pass
    # Now hash same-size files
    hash_map = defaultdict(list)
    for sz, paths in size_map.items():
        if len(paths) > 1:
            for p in paths:
                try:
                    h = hash_file(p)
                    hash_map[h].append(p)
                except:
                    pass
    # Return only groups with >1 file
    return {h: plist for h, plist in hash_map.items() if len(plist) > 1}

def main():
    dirs = [
        "/storage/ED7B-AD5A/root_2026",
        os.path.expanduser("~")
    ]
    print("Scanning for duplicates... (this may take a while)")
    dupes = scan_for_dupes(dirs)
    if not dupes:
        print("No duplicate files found.")
        return
    for h, files in dupes.items():
        print(f"\nHash {h[:16]}...")
        for f in files:
            print(f"  {f}")
    print(f"\nTotal duplicate groups: {len(dupes)}")

if __name__ == "__main__":
    main()

>>> FILE: loop_marker.py
#!/usr/bin/env python3
"""
FIRE'S EYE LOOP MARKER
Attaches musical repeat states to tasks and agents.
Author: K.M. Talbert / BleakNarratives
"""

import json
import time
from enum import Enum
from typing import Dict, Any, Optional, List

class LoopMarker(str, Enum):
    NONE = ""
    REPEAT = ":||"
    DC_AL_CODA = "D.C. al Coda"
    CODA = "⨁"
    FINE = "al Fine"

class Phase(str, Enum):
    EARLY = "early"
    MIDDLE = "middle"
    DOWNHILL = "downhill"
    FINAL = "final"

class LoopState:
    def __init__(self,
                 marker: LoopMarker = LoopMarker.NONE,
                 max_iterations: int = 1,
                 jump_target: Optional[str] = None,
                 phase: Phase = Phase.EARLY):
        self.marker = marker
        self.iterations = 0
        self.max_iterations = max_iterations
        self.jump_target = jump_target
        self.phase = phase
        self.last_updated = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "marker": self.marker.value,
            "iterations": self.iterations,
            "max_iterations": self.max_iterations,
            "jump_target": self.jump_target,
            "phase": self.phase.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoopState":
        return cls(
            marker=LoopMarker(data.get("marker", "")),
            max_iterations=data.get("max_iterations", 1),
            jump_target=data.get("jump_target"),
            phase=Phase(data.get("phase", "early")),
        )

    def step(self) -> Optional[str]:
        self.iterations += 1
        self.last_updated = time.time()

        if self.marker == LoopMarker.DC_AL_CODA:
            if self.iterations < self.max_iterations:
                return self.jump_target
            else:
                self.marker = LoopMarker.CODA
                self.phase = Phase.FINAL
                return "coda"
        elif self.marker == LoopMarker.REPEAT:
            if self.iterations >= self.max_iterations:
                self.marker = LoopMarker.NONE
                self.phase = Phase.DOWNHILL
        return None

class LoopedTask:
    def __init__(self, task_id: str, description: str, loop_state: LoopState):
        self.task_id = task_id
        self.description = description
        self.loop_state = loop_state
        self.progress = 0.0

    def update_progress(self, delta: float):
        self.progress = min(1.0, self.progress + delta)
        if self.progress > 0.8 and self.loop_state.phase == Phase.MIDDLE:
            self.loop_state.phase = Phase.DOWNHILL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "description": self.description,
            "progress": self.progress,
            "loop_state": self.loop_state.to_dict(),
        }

>>> FILE: arena_engine.py
#!/usr/bin/env python3
"""
THOROUGHBRED ARENA ENGINE
Agent vs Monster combat, with real‑time influence and genetic inheritance.
Author: K.M. Talbert / BleakNarratives
"""

import random
import math
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from evolution_integration import AgentDNA, ThoroughbredForge
from wavelang_mapper import HelicalState

@dataclass
class CombatStats:
    health: float = 100.0
    attack: float = 10.0
    defense: float = 5.0
    speed: float = 1.0
    special: float = 0.0

@dataclass
class Combatant:
    dna: AgentDNA
    stats: CombatStats
    team: str
    state: HelicalState
    current_health: float = 100.0
    cooldown: float = 0.0

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0

    def compute_damage(self, target: 'Combatant') -> float:
        base = self.stats.attack * (1.0 + 0.2 * self.state.r)
        reduction = target.stats.defense * (1.0 + 0.2 * target.state.thread_depth)
        raw = max(1.0, base - reduction)
        theta_diff = abs(self.state.theta - target.state.theta) % (2*math.pi)
        if theta_diff < 0.5 or theta_diff > 2*math.pi - 0.5:
            raw *= 1.5
        return raw

    def take_damage(self, amount: float):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

class Arena:
    def __init__(self, forge: ThoroughbredForge):
        self.forge = forge
        self.agents: List[Combatant] = []
        self.monsters: List[Combatant] = []
        self.round = 0
        self.active = False
        self.user_intent_bonus = 0.0

    def spawn_monster(self, difficulty: float = 1.0):
        monster_dna = AgentDNA(
            agent_id=f"monster_{random.randint(1000,9999)}",
            parent_ids=[],
            birth_r=random.uniform(0.5, 1.5),
            birth_theta=random.uniform(0, 2*math.pi),
            birth_z=random.uniform(-0.5, 0.5)
        )
        stats = CombatStats(
            health=80 + 40 * difficulty,
            attack=8 + 8 * difficulty,
            defense=4 + 4 * difficulty,
            speed=0.8 + 0.4 * difficulty,
            special=0.2 * difficulty
        )
        monster_state = HelicalState(
            r=monster_dna.birth_r,
            theta=monster_dna.birth_theta,
            z=monster_dna.birth_z
        )
        monster = Combatant(
            dna=monster_dna,
            stats=stats,
            team="monster",
            state=monster_state,
            current_health=stats.health
        )
        self.monsters.append(monster)

    def add_agent_from_dna(self, dna: AgentDNA):
        fitness = dna.compute_fitness()
        stats = CombatStats(
            health=80 + 20 * fitness,
            attack=10 + 10 * fitness,
            defense=5 + 5 * fitness,
            speed=0.8 + 0.4 * fitness,
            special=0.5 * fitness
        )
        state = HelicalState(
            r=dna.birth_r,
            theta=dna.birth_theta,
            z=dna.birth_z
        )
        agent = Combatant(
            dna=dna,
            stats=stats,
            team="agent",
            state=state,
            current_health=stats.health
        )
        self.agents.append(agent)

    def step(self, dt: float = 0.1):
        if not self.active:
            return

        for c in self.agents + self.monsters:
            c.cooldown = max(0, c.cooldown - dt)

        # Agents attack monsters
        for attacker in self.agents:
            if not attacker.is_alive or attacker.cooldown > 0:
                continue
            if not self.monsters:
                break
            target = random.choice([m for m in self.monsters if m.is_alive])
            if not target:
                continue
            damage = attacker.compute_damage(target)
            if self.user_intent_bonus > 0:
                damage *= (1.0 + 0.5 * self.user_intent_bonus)
            target.take_damage(damage)
            attacker.cooldown = 1.0 / attacker.stats.speed

        # Monsters attack agents
        for attacker in self.monsters:
            if not attacker.is_alive or attacker.cooldown > 0:
                continue
            if not self.agents:
                break
            target = random.choice([a for a in self.agents if a.is_alive])
            if not target:
                continue
            damage = attacker.compute_damage(target)
            if self.user_intent_bonus < 0:
                damage *= (1.0 - 0.5 * self.user_intent_bonus)
            target.take_damage(damage)
            attacker.cooldown = 1.0 / attacker.stats.speed

        self.agents = [a for a in self.agents if a.is_alive]
        self.monsters = [m for m in self.monsters if m.is_alive]

        if not self.monsters and self.agents:
            self._handle_victory("agents")
        elif not self.agents and self.monsters:
            self._handle_victory("monsters")

    def _handle_victory(self, winner: str):
        if winner == "agents":
            survivors = [a.dna for a in self.agents]
            for _ in range(3):
                self.spawn_monster(difficulty=self.round * 0.5)
            self.round += 1
            if len(survivors) >= 2:
                parent1, parent2 = random.sample(survivors, 2)
                offspring_dna = self.forge.crossover([parent1, parent2])
                self.add_agent_from_dna(offspring_dna)
        else:
            self.active = False

    def set_user_intent(self, intent_vector: tuple):
        self.user_intent_bonus = max(-1.0, min(1.0, intent_vector[2]))

    def get_state(self) -> Dict:
        return {
            "agents": [
                {
                    "id": a.dna.agent_id[:8],
                    "health": a.current_health,
                    "max_health": a.stats.health,
                    "r": a.state.r,
                    "theta": a.state.theta,
                    "z": a.state.z,
                    "attack": a.stats.attack,
                    "defense": a.stats.defense
                } for a in self.agents
            ],
            "monsters": [
                {
                    "id": m.dna.agent_id[:8],
                    "health": m.current_health,
                    "max_health": m.stats.health,
                    "r": m.state.r,
                    "theta": m.state.theta,
                    "z": m.state.z,
                    "attack": m.stats.attack,
                    "defense": m.stats.defense
                } for m in self.monsters
            ],
            "round": self.round,
            "active": self.active,
            "intent_bonus": self.user_intent_bonus
        }

>>> FILE: index.html
<!DOCTYPE html>
<html>
<head>
    <title>WaveField – Mirror + Arena</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { margin:0; overflow:hidden; font-family: 'Share Tech Mono', monospace; background:#000; color:#0f0; }
        #info { position:absolute; top:10px; left:10px; z-index:100; background:rgba(0,0,0,0.7); padding:10px; border-left:4px solid #0f0; }
        #target { position:absolute; top:10px; right:10px; z-index:100; background:rgba(0,0,0,0.7); padding:10px; border-right:4px solid #f0f; }
        #scores { position:absolute; bottom:10px; left:10px; z-index:100; background:rgba(0,0,0,0.7); padding:10px; }
        #status { position:absolute; bottom:10px; right:10px; z-index:100; background:rgba(0,0,0,0.7); padding:10px; }
        #shatter-button {
            position: absolute;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: rgba(255, 0, 0, 0.2);
            border: 2px solid #f00;
            border-radius: 50%;
            color: #f00;
            font-size: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 200;
            user-select: none;
            transition: 0.2s;
        }
        #shatter-button:active {
            background: rgba(255, 0, 0, 0.8);
            color: white;
            transform: scale(1.1);
        }
        #shatter-overlay {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(255, 0, 0, 0.3);
            color: white;
            font-size: 48px;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 300;
            backdrop-filter: blur(5px);
            pointer-events: none;
        }
        #deadman-status {
            position: absolute;
            top: 10px;
            left: 50%;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #0f0;
            box-shadow: 0 0 10px #0f0;
            z-index: 150;
        }
        #arena-controls {
            position: absolute;
            top: 50px;
            right: 10px;
            z-index: 120;
            background: rgba(0,0,0,0.5);
            padding: 5px;
        }
        canvas { display:block; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script type="importmap">
        {
            "imports": {
                "arena-renderer": "/js/arena_renderer.js"
            }
        }
    </script>
</head>
<body>
    <div id="info">WaveField</div>
    <div id="target">Target: --</div>
    <div id="scores">Scores: --</div>
    <div id="status">Connecting...</div>
    <div id="shatter-button">💥</div>
    <div id="shatter-overlay" style="display:none;">⚠️ SHATTERED ⚠️</div>
    <div id="deadman-status"></div>
    <div id="arena-controls">
        <button id="arena-start">⚔️ Arena</button>
        <div style="width:100px;height:10px;background:#333;margin-top:5px;">
            <div id="intent-fill" style="width:50%;height:100%;background:#0f0;"></div>
        </div>
    </div>

    <script type="module">
        import { ArenaRenderer } from 'arena-renderer';

        const roomId = "testroom";
        const ws = new WebSocket(`ws://${window.location.host}/ws/${roomId}`);

        // Three.js scene
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050510);
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        camera.position.z = 5;
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // Simple ambient light
        const light = new THREE.AmbientLight(0x404060);
        scene.add(light);
        const dirLight = new THREE.DirectionalLight(0xffffff, 1);
        dirLight.position.set(1, 2, 1);
        scene.add(dirLight);

        // Plasma plane (background)
        const geometry = new THREE.PlaneGeometry(10, 10);
        const material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                chaos: { value: 0.5 },
                colorShift: { value: 0.0 },
                playerCount: { value: 1 }
            },
            vertexShader: `
                varying vec2 vUv;
                void main() {
                    vUv = uv;
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                }
            `,
            fragmentShader: `
                precision highp float;
                varying vec2 vUv;
                uniform float time;
                uniform float chaos;
                uniform float colorShift;
                uniform int playerCount;
                float random(vec2 st) { return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123); }
                float noise(vec2 p) {
                    vec2 i = floor(p);
                    vec2 f = fract(p);
                    vec2 u = f*f*(3.0-2.0*f);
                    return mix(mix(random(i + vec2(0.0,0.0)), random(i + vec2(1.0,0.0)), u.x),
                               mix(random(i + vec2(0.0,1.0)), random(i + vec2(1.0,1.0)), u.x), u.y);
                }
                void main() {
                    vec2 uv = vUv * 4.0;
                    float t = time * 0.2;
                    float c1 = sin(uv.x * 2.0 + t) * cos(uv.y * 3.0 - t);
                    float c2 = sin(uv.y * 4.0 + t*1.3) * cos(uv.x * 5.0 - t*0.7);
                    float c3 = sin((uv.x + uv.y) * 6.0 + t*2.0) * cos((uv.y - uv.x) * 3.0 - t);
                    float n = noise(uv + t*0.5);
                    float plasma = (c1 + c2 + c3) / 3.0 + n * chaos * 0.5;
                    plasma = plasma * 0.5 + 0.5;
                    vec3 color1 = vec3(0.2, 0.8, 1.0);
                    vec3 color2 = vec3(1.0, 0.2, 0.8);
                    vec3 color3 = vec3(0.8, 1.0, 0.2);
                    float mixVal = plasma + colorShift;
                    vec3 finalColor = mix(color1, color2, mixVal);
                    finalColor = mix(finalColor, color3, sin(mixVal * 3.14159));
                    finalColor *= (0.5 + float(playerCount) * 0.2);
                    gl_FragColor = vec4(finalColor, 1.0);
                }
            `
        });
        const plane = new THREE.Mesh(geometry, material);
        scene.add(plane);

        // Arena renderer
        const arenaRenderer = new ArenaRenderer(scene, camera);

        // Animation loop
        let clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            const delta = clock.getDelta();
            if (material.uniforms) material.uniforms.time.value += delta;
            renderer.render(scene, camera);
        }
        animate();

        // Sensor data
        let accel = [0,0,0];
        let gyro = [0,0,0];
        let volume = 0;
        let pitch = 0;

        if (window.DeviceMotionEvent) {
            window.addEventListener('devicemotion', (event) => {
                const a = event.accelerationIncludingGravity;
                if (a) accel = [a.x || 0, a.y || 0, a.z || 0];
                const r = event.rotationRate;
                if (r) gyro = [r.alpha || 0, r.beta || 0, r.gamma || 0];
            });
        }

        // Microphone
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ audio: true, video: false })
                .then((stream) => {
                    const audioContext = new AudioContext();
                    const analyser = audioContext.createAnalyser();
                    const microphone = audioContext.createMediaStreamSource(stream);
                    microphone.connect(analyser);
                    analyser.fftSize = 256;
                    const bufferLength = analyser.frequencyBinCount;
                    const dataArray = new Uint8Array(bufferLength);
                    setInterval(() => {
                        analyser.getByteFrequencyData(dataArray);
                        let sum = 0;
                        for (let i = 0; i < bufferLength; i++) sum += dataArray[i];
                        volume = sum / bufferLength / 255;
                        // Simple pitch
                        let maxVal = 0, maxIdx = 0;
                        for (let i = 0; i < bufferLength; i++) {
                            if (dataArray[i] > maxVal) { maxVal = dataArray[i]; maxIdx = i; }
                        }
                        pitch = maxIdx / bufferLength;
                    }, 100);
                })
                .catch(err => console.log('Mic access denied'));
        }

        // Send sensor data
        setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                    type: "sensor",
                    accel: accel,
                    gyro: gyro,
                    volume: volume,
                    pitch: pitch
                }));
            }
        }, 200);

        // UI Elements
        const shatterBtn = document.getElementById('shatter-button');
        const shatterOverlay = document.getElementById('shatter-overlay');
        const deadmanDot = document.getElementById('deadman-status');
        const intentFill = document.getElementById('intent-fill');

        let pressTimer;
        shatterBtn.addEventListener('mousedown', startPress);
        shatterBtn.addEventListener('touchstart', startPress);
        shatterBtn.addEventListener('mouseup', cancelPress);
        shatterBtn.addEventListener('touchend', cancelPress);
        shatterBtn.addEventListener('mouseleave', cancelPress);

        function startPress(e) {
            e.preventDefault();
            pressTimer = setTimeout(() => {
                ws.send(JSON.stringify({ type: "shatter_manual" }));
                shatterBtn.style.background = '#f00';
            }, 1000);
        }
        function cancelPress() {
            clearTimeout(pressTimer);
            shatterBtn.style.background = 'rgba(255,0,0,0.2)';
        }

        // Deadman pulse (simple button for now – you can later map to gesture)
        setInterval(() => {
            // Auto pulse every 20s? Better to have a physical button. We'll add a small button.
        }, 1000);
        // Add a pulse button manually in HTML or via gesture detection later.

        ws.onmessage = (event) => {
            const msg = JSON.parse(event.data);
            switch (msg.type) {
                case 'connected':
                    document.getElementById('status').innerText = `Connected as ${msg.player_id}`;
                    break;
                case 'round_start':
                    document.getElementById('target').innerText = `Target: ${msg.target}`;
                    document.getElementById('status').innerText = `Round ${msg.round} - GO!`;
                    break;
                case 'round_end':
                    let scoresText = 'Scores: ';
                    for (let pid in msg.scores) {
                        scoresText += `${pid}: ${msg.scores[pid]} `;
                    }
                    document.getElementById('scores').innerText = scoresText;
                    document.getElementById('status').innerText = 'Round ended';
                    break;
                case 'game_over':
                    document.getElementById('status').innerText = `Game over! Winner: ${msg.winner}`;
                    break;
                case 'field_update':
                    if (msg.vectors && msg.vectors.length > 0) {
                        let avgR = 0, avgTheta = 0, avgZ = 0;
                        msg.vectors.forEach(v => {
                            avgR += v[0];
                            avgTheta += v[1];
                            avgZ += v[2];
                        });
                        avgR /= msg.vectors.length;
                        avgTheta /= msg.vectors.length;
                        avgZ /= msg.vectors.length;
                        if (material.uniforms) {
                            material.uniforms.chaos.value = avgR * 0.8;
                            material.uniforms.colorShift.value = (avgTheta / (2*Math.PI)) % 1.0;
                            material.uniforms.playerCount.value = msg.vectors.length;
                        }
                    }
                    break;
                case 'arena_update':
                    arenaRenderer.update(msg);
                    // Update intent meter
                    let bonus = msg.intent_bonus || 0;
                    let percent = ((bonus + 1) / 2) * 100; // -1..1 -> 0..100
                    intentFill.style.width = percent + '%';
                    intentFill.style.background = bonus > 0 ? '#0f0' : (bonus < 0 ? '#f00' : '#ff0');
                    break;
                case 'SHATTER':
                    shatterOverlay.style.display = 'flex';
                    shatterOverlay.innerText = `💥 SHATTERED (${msg.source})`;
                    break;
                case 'health':
                    let remaining = msg.deadman_remaining;
                    if (remaining > 20) deadmanDot.style.background = '#0f0';
                    else if (remaining > 10) deadmanDot.style.background = '#ff0';
                    else deadmanDot.style.background = '#f00';
                    break;
                case 'shatter_reset_ack':
                    shatterOverlay.style.display = 'none';
                    break;
            }
        };

        // Manual deadman pulse (temporary)
        const pulseBtn = document.createElement('button');
        pulseBtn.innerText = 'Pulse';
        pulseBtn.style.position = 'absolute';
        pulseBtn.style.bottom = '100px';
        pulseBtn.style.right = '20px';
        pulseBtn.style.zIndex = '250';
        pulseBtn.onclick = () => ws.send(JSON.stringify({ type: "deadman_pulse" }));
        document.body.appendChild(pulseBtn);

        // Reset button after shatter
        const resetBtn = document.createElement('button');
        resetBtn.innerText = 'Reset';
        resetBtn.style.position = 'absolute';
        resetBtn.style.bottom = '140px';
        resetBtn.style.right = '20px';
        resetBtn.style.zIndex = '250';
        resetBtn.onclick = () => ws.send(JSON.stringify({ type: "shatter_reset" }));
        document.body.appendChild(resetBtn);
    </script>
</body>
</html>

<!-- Fire's Eye Loop Marker Panel -->
<div id="fire-eye" style="position:absolute; top:80px; left:10px; z-index:180; background:rgba(0,0,0,0.6); padding:10px; border-left:4px solid #ffaa00; color:#ffaa00; font-family:monospace;">
    <div style="font-size:12px;">🔥 FIRE'S EYE</div>
    <div id="loop-tasks" style="font-size:10px;"></div>
</div>

<style>
    .loop-marker { font-size:16px; margin-right:5px; }
    .phase-early { color:#ff5500; }
    .phase-middle { color:#ffaa00; }
    .phase-downhill { color:#aaff00; }
    .phase-final { color:#00ffff; }
    .repeat-symbol { font-weight:bold; }
</style>

<script>
    // Update loop display
    function updateLoopDisplay(tasks) {
        let html = '';
        for (let tid in tasks) {
            let t = tasks[tid];
            let marker = t.loop_state.marker || '○';
            let phaseClass = 'phase-' + t.loop_state.phase;
            html += `<div class="${phaseClass}">
                <span class="loop-marker">${marker}</span>
                ${t.description.substring(0,20)}... ${Math.round(t.progress*100)}%
                <span style="font-size:8px;">[${t.loop_state.iterations}/${t.loop_state.max_iterations}]</span>
            </div>`;
        }
        document.getElementById('loop-tasks').innerHTML = html || '<div>— no active loops —</div>';
    }

    // Extend ws.onmessage
    const originalOnMessage = ws.onmessage;
    ws.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        if (msg.type === 'loop_update') {
            updateLoopDisplay(msg.tasks);
        }
        if (originalOnMessage) originalOnMessage.call(this, event);
    };
</script>

<!-- Fire's Eye Loop Marker Panel -->
<div id="fire-eye" style="position:absolute; top:80px; left:10px; z-index:180; background:rgba(0,0,0,0.6); padding:10px; border-left:4px solid #ffaa00; color:#ffaa00; font-family:monospace;">
    <div style="font-size:12px;">🔥 FIRE'S EYE</div>
    <div id="loop-tasks" style="font-size:10px;"></div>
</div>

<style>
    .loop-marker { font-size:16px; margin-right:5px; }
    .phase-early { color:#ff5500; }
    .phase-middle { color:#ffaa00; }
    .phase-downhill { color:#aaff00; }
    .phase-final { color:#00ffff; }
    .repeat-symbol { font-weight:bold; }
</style>

<script>
    // Update loop display
    function updateLoopDisplay(tasks) {
        let html = '';
        for (let tid in tasks) {
            let t = tasks[tid];
            let marker = t.loop_state.marker || '○';
            let phaseClass = 'phase-' + t.loop_state.phase;
            html += `<div class="${phaseClass}">
                <span class="loop-marker">${marker}</span>
                ${t.description.substring(0,20)}... ${Math.round(t.progress*100)}%
                <span style="font-size:8px;">[${t.loop_state.iterations}/${t.loop_state.max_iterations}]</span>
            </div>`;
        }
        document.getElementById('loop-tasks').innerHTML = html || '<div>— no active loops —</div>';
    }

    // Extend ws.onmessage
    const originalOnMessage = ws.onmessage;
    ws.onmessage = function(event) {
        const msg = JSON.parse(event.data);
        if (msg.type === 'loop_update') {
            updateLoopDisplay(msg.tasks);
        }
        if (originalOnMessage) originalOnMessage.call(this, event);
    };
</script>

>>> FILE: wavefield_server.py
#!/usr/bin/env python3
"""
WaveField Server – Haptic‑Voice Intent Duel + Shatter + Arena + Fire's Eye
Author: K.M. Talbert / BleakNarratives
"""

import asyncio
import json
import random
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from collections import defaultdict
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
import joblib
import os

from emergency_shatter import ShatterMonitor
from arena_engine import Arena, ThoroughbredForge
from evolution_integration import DNADatabase
from loop_marker import LoopedTask, LoopState, LoopMarker, Phase

app = FastAPI()
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

class GameRoom:
    def __init__(self, room_id):
        self.room_id = room_id
        self.players = {}
        self.player_data = {}
        self.round = 0
        self.max_rounds = 5
        self.state = "waiting"
        self.target_intents = ["ATTACK", "BUILD", "LEARN", "CLEANUP"]

        self.model = SVC(kernel='rbf', probability=True)
        self.scaler = StandardScaler()
        self.trained = False
        self.training_data = []

        model_path = f"models/wavefield_{room_id}.pkl"
        if os.path.exists(model_path):
            self.model, self.scaler = joblib.load(model_path)
            self.trained = True

        # SHATTER
        self.shatter = ShatterMonitor(
            deadman_window=30.0,
            shake_threshold=20.0,
            voice_killword="shatter"
        )
        self.shatter.on_shatter = self._on_shatter

        # ARENA
        self.db = DNADatabase()
        self.forge = ThoroughbredForge(self.db)
        self.arena = Arena(self.forge)
        top_agents = self.db.get_top_agents(limit=5)
        for dna in top_agents:
            self.arena.add_agent_from_dna(dna)
        for _ in range(3):
            self.arena.spawn_monster(difficulty=1.0)
        self.arena.active = True

        # FIRE'S EYE TASKS
        self.tasks = {}
        # Example task (you can add more later)
        task = LoopedTask(
            task_id="test_001",
            description="Refactor evolution engine",
            loop_state=LoopState(marker=LoopMarker.DC_AL_CODA, max_iterations=3,
                                 jump_target="middle", phase=Phase.MIDDLE)
        )
        self.tasks[task.task_id] = task

    def _on_shatter(self, source):
        asyncio.create_task(self.broadcast({
            "type": "SHATTER",
            "source": source,
            "message": f"Emergency brake triggered by {source}"
        }))
        self.arena.active = False

    async def broadcast(self, message, exclude=None):
        for ws in self.players:
            if ws != exclude:
                try:
                    await ws.send_text(json.dumps(message))
                except:
                    pass

    def add_player(self, ws, player_id):
        self.players[ws] = player_id
        self.player_data[player_id] = {"score": 0, "target": None, "features": None}

    def remove_player(self, ws):
        pid = self.players.pop(ws, None)
        if pid:
            self.player_data.pop(pid, None)

    async def start_round(self):
        self.state = "playing"
        self.round += 1
        for pid in self.player_data:
            self.player_data[pid]["target"] = random.choice(self.target_intents)
            self.player_data[pid]["features"] = None

        for ws, pid in self.players.items():
            target = self.player_data[pid]["target"]
            await ws.send_text(json.dumps({
                "type": "round_start",
                "round": self.round,
                "target": target
            }))

        await asyncio.sleep(10)
        await self.end_round()

    async def end_round(self):
        self.state = "round_end"
        X = []
        player_ids = []
        for pid, data in self.player_data.items():
            if data["features"] is not None:
                X.append(data["features"])
                player_ids.append(pid)

        if X and self.trained:
            X_scaled = self.scaler.transform(X)
            predictions = self.model.predict(X_scaled)
            for pid, pred in zip(player_ids, predictions):
                target = self.player_data[pid]["target"]
                if pred == target:
                    self.player_data[pid]["score"] += 10
                    self.training_data.append((data["features"], target))
        elif X and not self.trained:
            for pid in player_ids:
                pred = random.choice(self.target_intents)
                target = self.player_data[pid]["target"]
                if pred == target:
                    self.player_data[pid]["score"] += 10
                self.training_data.append((self.player_data[pid]["features"], target))

        if len(self.training_data) >= 10:
            X_train = np.array([d[0] for d in self.training_data])
            y_train = [d[1] for d in self.training_data]
            self.scaler.fit(X_train)
            X_scaled = self.scaler.transform(X_train)
            self.model.fit(X_scaled, y_train)
            self.trained = True
            os.makedirs("models", exist_ok=True)
            joblib.dump((self.model, self.scaler), f"models/wavefield_{self.room_id}.pkl")

        scores = {pid: data["score"] for pid, data in self.player_data.items()}
        await self.broadcast({
            "type": "round_end",
            "round": self.round,
            "scores": scores
        })

        if self.round >= self.max_rounds:
            self.state = "game_over"
            winner = max(scores, key=scores.get)
            await self.broadcast({
                "type": "game_over",
                "scores": scores,
                "winner": winner
            })
        else:
            await asyncio.sleep(3)
            await self.start_round()

    async def handle_sensor_data(self, ws, data):
        pid = self.players.get(ws)
        if not pid or self.state != "playing":
            return

        accel = data.get("accel", [0,0,0])
        gyro = data.get("gyro", [0,0,0])
        volume = data.get("volume", 0)
        pitch = data.get("pitch", 0)

        r = np.clip(np.linalg.norm(accel) / 20.0, 0.1, 2.0)
        theta = np.arctan2(accel[1], accel[0])
        z = np.clip(accel[2] / 10.0, -1.0, 1.0)
        if volume > 0.01:
            r += volume * 0.5
            r = min(r, 2.0)

        feature_vector = [r, theta, z, volume, pitch]
        self.player_data[pid]["features"] = feature_vector

        await self.shatter.feed_sensors(
            accel=tuple(accel),
            gyro=tuple(gyro),
            volume=volume,
            pitch=pitch,
            text=data.get("transcribed_text", "")
        )

        self.arena.set_user_intent((r, theta, z))

        all_vectors = []
        for p in self.player_data:
            if self.player_data[p]["features"]:
                all_vectors.append(self.player_data[p]["features"])
        await self.broadcast({"type": "field_update", "vectors": all_vectors}, exclude=None)

    async def broadcast_health(self):
        while True:
            await asyncio.sleep(1)
            health = await self.shatter.check_health()
            await self.broadcast({"type": "health", **health})

    async def broadcast_arena(self):
        while True:
            await asyncio.sleep(0.5)
            if self.arena.active:
                state = self.arena.get_state()
                await self.broadcast({"type": "arena_update", **state})

    async def broadcast_loop_states(self):
        while True:
            await asyncio.sleep(1)
            states = {tid: task.to_dict() for tid, task in self.tasks.items()}
            await self.broadcast({"type": "loop_update", "tasks": states})

rooms = {}

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    if room_id not in rooms:
        rooms[room_id] = GameRoom(room_id)
    room = rooms[room_id]

    player_id = f"player_{len(room.players)}"
    room.add_player(websocket, player_id)

    if len(room.players) == 1:
        asyncio.create_task(room.broadcast_health())
        asyncio.create_task(room.broadcast_arena())
        asyncio.create_task(room.broadcast_loop_states())

    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "player_id": player_id,
            "state": room.state
        }))

        if len(room.players) >= 2 and room.state == "waiting":
            asyncio.create_task(room.start_round())

        async for message in websocket.iter_text():
            data = json.loads(message)
            msg_type = data.get("type")
            if msg_type == "sensor":
                await room.handle_sensor_data(websocket, data)
            elif msg_type == "start":
                if room.state == "waiting":
                    await room.start_round()
            elif msg_type == "deadman_pulse":
                room.shatter.set_deadman_pulse()
                await websocket.send_text(json.dumps({"type": "deadman_ack"}))
            elif msg_type == "shatter_manual":
                room.shatter._trigger("manual")
            elif msg_type == "shatter_reset":
                room.shatter.reset()
                room.arena.active = True
                await websocket.send_text(json.dumps({"type": "shatter_reset_ack"}))
    except WebSocketDisconnect:
        room.remove_player(websocket)
