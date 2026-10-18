"""
Tree Renderer - Organic growth visualization
ASCII art that grows as molt iterates
"""

import os
import sys
import time
from typing import List

class TreeRenderer:
    def __init__(self):
        self.width = 80
        self.height = 24
        self.branches = []
        self.leaves = []
        
    def clear(self):
        """Clear terminal"""
        os.system('clear' if os.name != 'nt' else 'cls')
        
    def plant_seed(self, task: str):
        """Show initial seed/task"""
        self._print_centered("🌱")
        self._print_centered(f"Seed: {task[:50]}...")
        print()
        
    def show_growth_ring(self, iteration: int):
        """Show iteration number as growth ring"""
        ring = f"═══ Ring {iteration} ═══"
        self._print_centered(ring)
        
    def grow_branch(self, iteration: int, content: str, score: float):
        """Add a branch to the tree"""
        self.branches.append({
            'iteration': iteration,
            'content': content,
            'score': score
        })
        
        # Visual branch based on score
        branch_char = "┃" if score > 0.7 else "│"
        leaf_char = "●" if score > 0.7 else "○"
        
        # Alternate sides for visual interest
        indent = "  " * (iteration % 4)
        if iteration % 2 == 0:
            print(f"{indent}{branch_char}──{leaf_char} [{score:.2f}] {content[:40]}...")
        else:
            spaces = " " * (self.width - len(indent) - 50)
            print(f"{spaces}{leaf_char}──{branch_char} [{score:.2f}] {content[:40]}...")
    
    def bloom_leaf(self, iteration: int):
        """Mark an improvement with a blooming leaf"""
        self.leaves.append(iteration)
        self._print_centered("🌿 Improvement detected!")
        
    def show_canopy(self):
        """Show final tree canopy"""
        print("\n")
        canopy = [
            "        🌳",
            "       /|\\",
            "      / | \\",
            "     /  |  \\",
            "    ────┴────"
        ]
        for line in canopy:
            self._print_centered(line)
        
        print()
        self._print_centered(f"Total branches: {len(self.branches)}")
        self._print_centered(f"Improvements: {len(self.leaves)}")
    
    def _print_centered(self, text: str):
        """Print centered text"""
        padding = (self.width - len(text)) // 2
        print(" " * padding + text)


class OrganicRenderer:
    """Alternative renderer - more abstract/organic"""
    
    def __init__(self):
        self.symbols = {
            'root': '◉',
            'branch': '╱╲│',
            'leaf': '●○◐◑',
            'bloom': '✿❀✾',
            'fruit': '◆◇'
        }
        
    def render_growth(self, iteration: int, data: dict):
        """Render organic growth pattern"""
        # Could implement fractal-like patterns
        # Fibonacci spiral layouts
        # Or other organic arrangements
        pass


class SpiralRenderer:
    """Spiral output renderer - text curves outward"""
    
    def __init__(self, center_x: int = 40, center_y: int = 12):
        self.center_x = center_x
        self.center_y = center_y
        self.angle = 0
        self.radius = 1
        
    def spiral_print(self, text: str):
        """Print text in spiral pattern"""
        import math
        
        for char in text:
            # Calculate position on spiral
            x = int(self.center_x + self.radius * math.cos(self.angle))
            y = int(self.center_y + self.radius * math.sin(self.angle))
            
            # Move cursor and print (would need curses for proper positioning)
            print(f"\033[{y};{x}H{char}", end='', flush=True)
            
            # Increment spiral
            self.angle += 0.3
            self.radius += 0.05
            time.sleep(0.01)
