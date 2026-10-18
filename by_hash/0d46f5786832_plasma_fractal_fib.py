#!/usr/bin/env python3
"""
Fractal Plasma + Fibonacci Wave Visualizer
For Termux / any 256‑color terminal.
Falling and ascending, as above so below.
"""

import curses
import math
import time
import sys

def main(stdscr):
    # Setup
    curses.curs_set(0)               # Hide cursor
    curses.use_default_colors()
    # Initialize 256 color pairs (fg = color index, bg = default)
    for i in range(256):
        curses.init_pair(i, i, -1)
    stdscr.nodelay(1)                 # Non‑blocking input
    stdscr.timeout(0)

    # Get terminal size
    max_y, max_x = stdscr.getmaxyx()
    # We'll draw inside these bounds, avoid last line to prevent scroll
    draw_y = max_y - 1
    draw_x = max_x

    # Precompute character ramp: darker to brighter (classic plasma chars)
    chars = " .-~+=*!?#$%&@"
    char_step = 255 / (len(chars) - 1)

    # Golden ratio for Fibonacci spice
    phi = (1 + math.sqrt(5)) / 2
    t = 0.0

    try:
        while True:
            # Check for 'q' to quit
            if stdscr.getch() == ord('q'):
                break

            # Clear screen
            stdscr.clear()

            # Loop over each cell
            for y in range(draw_y):
                for x in range(draw_x):
                    # Normalized coordinates (0 to 2π scale)
                    nx = x / draw_x * 4 * math.pi
                    ny = y / draw_y * 4 * math.pi

                    # Plasma function with Fibonacci (phi) modulations
                    v1 = math.sin(nx * 0.5 + t)
                    v2 = math.sin(ny * 0.5 + t * phi)
                    v3 = math.sin((nx + ny) * 0.3 + t * 0.7)
                    v4 = math.sin((nx * phi + ny / phi) * 0.4 + t * 1.3)

                    # Combine and map to 0..255
                    intensity = (v1 + v2 + v3 + v4) / 4.0  # -1..1
                    intensity = (intensity + 1) / 2.0 * 255  # 0..255

                    # Choose character based on intensity
                    char_idx = int(intensity / char_step)
                    char = chars[min(char_idx, len(chars)-1)]

                    # Color = intensity (direct mapping to 256‑color palette)
                    color_pair = curses.color_pair(int(intensity))

                    # Add character to screen
                    try:
                        stdscr.addch(y, x, char, color_pair)
                    except curses.error:
                        # Ignore writing errors at screen edges
                        pass

            # Refresh screen
            stdscr.refresh()
            t += 0.05  # speed
            time.sleep(0.03)  # frame rate

    except KeyboardInterrupt:
        pass
    finally:
        # Cleanup
        curses.endwin()

if __name__ == "__main__":
    # Ensure terminal has 256 colors
    curses.wrapper(main)