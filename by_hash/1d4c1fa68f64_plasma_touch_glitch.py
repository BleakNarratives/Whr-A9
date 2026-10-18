#!/usr/bin/env python3
"""
Terminal plasma with tilt‑sensitive glitch.
Requires Termux:API and a device with accelerometer.
Run with: python plasma_touch_glitch.py
"""

import curses
import math
import time
import sys
import threading
import subprocess
import json
from queue import Queue, Empty

# ----------------------------------------------------------------------
# Tilt detection via Termux:API (runs in background thread)
# ----------------------------------------------------------------------
tilt_queue = Queue()  # stores latest tilt magnitude (0-1)
glitch_duration = 0    # frames remaining for glitch effect

def tilt_listener():
    """Continuously read accelerometer and push magnitude to queue."""
    while True:
        try:
            # Run termux-sensor once, get accelerometer data
            result = subprocess.run(
                ["termux-sensor", "-s", "TYPE_ACCELEROMETER", "-n", "1"],
                capture_output=True, text=True, timeout=0.5
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                # Extract acceleration values (x, y, z)
                accel = data.get("TYPE_ACCELEROMETER", {}).get("values", [0, 0, 0])
                # Compute magnitude (gravity ≈ 9.8, so 1g = 9.8)
                mag = math.sqrt(accel[0]**2 + accel[1]**2 + accel[2]**2) / 9.8
                # Clip and push to queue (replace old value)
                tilt_queue.put(min(mag, 2.0))
        except Exception:
            pass
        time.sleep(0.05)  # 20 Hz sampling

# Start listener thread
listener_thread = threading.Thread(target=tilt_listener, daemon=True)
listener_thread.start()

# ----------------------------------------------------------------------
# Main visualizer
# ----------------------------------------------------------------------
def main(stdscr):
    global glitch_duration

    # Setup curses
    curses.curs_set(0)
    curses.use_default_colors()
    # Initialize 256 color pairs (fg = color index, bg = default)
    for i in range(256):
        curses.init_pair(i, i, -1)
    stdscr.nodelay(1)
    stdscr.timeout(0)

    max_y, max_x = stdscr.getmaxyx()
    draw_y = max_y - 1
    draw_x = max_x

    # Brighter character ramp (includes more dense symbols)
    chars = " .-~+=*!?#$%&@█▓▒░"  # added block elements for extra brightness
    char_step = 255 / (len(chars) - 1)

    phi = (1 + math.sqrt(5)) / 2
    t = 0.0

    # Glitch state
    glitch = False
    glitch_timer = 0

    try:
        while True:
            # Check for quit ('q')
            if stdscr.getch() == ord('q'):
                break

            # Get latest tilt magnitude from queue
            tilt_mag = 1.0
            try:
                while True:
                    tilt_mag = tilt_queue.get_nowait()
            except Empty:
                pass

            # Trigger glitch if tilt exceeds threshold (e.g., >1.5g)
            if tilt_mag > 1.5 and glitch_duration <= 0:
                glitch_duration = 10  # frames
            if glitch_duration > 0:
                glitch = True
                glitch_duration -= 1
            else:
                glitch = False

            stdscr.clear()

            # Loop over each cell
            for y in range(draw_y):
                for x in range(draw_x):
                    # Normalized coordinates, modulated by tilt
                    freq = 4 * math.pi
                    if glitch:
                        # Glitch mode: distort frequencies randomly
                        freq *= (1.0 + (hash((x, y, int(t*10))) % 100) / 100 - 0.5)
                    nx = x / draw_x * freq
                    ny = y / draw_y * freq

                    # Wave functions with Fibonacci ratio
                    v1 = math.sin(nx * 0.5 + t)
                    v2 = math.sin(ny * 0.5 + t * phi)
                    v3 = math.sin((nx + ny) * 0.3 + t * 0.7)
                    v4 = math.sin((nx * phi + ny / phi) * 0.4 + t * 1.3)

                    intensity = (v1 + v2 + v3 + v4) / 4.0
                    intensity = (intensity + 1) / 2.0 * 255  # 0-255

                    if glitch:
                        # Glitch: invert and scramble
                        intensity = 255 - intensity
                        # Add noise
                        intensity += (hash((x, y, t)) % 50) - 25
                        intensity = max(0, min(255, intensity))

                    # Character selection
                    char_idx = int(intensity / char_step)
                    char = chars[min(char_idx, len(chars)-1)]

                    # Color: use intensity + bold for extra brightness
                    color = curses.color_pair(int(intensity)) | curses.A_BOLD

                    try:
                        stdscr.addch(y, x, char, color)
                    except curses.error:
                        pass

            stdscr.refresh()
            t += 0.05
            time.sleep(0.03)

    except KeyboardInterrupt:
        pass
    finally:
        curses.endwin()

if __name__ == "__main__":
    # Check if termux-sensor is available
    import shutil
    if shutil.which("termux-sensor") is None:
        print("Termux:API not installed. Please install: pkg install termux-api")
        print("Falling back to non‑tilt mode.")
        # We'll still run, but tilt will always be 1.0
    curses.wrapper(main)