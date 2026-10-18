#!/usr/bin/env python3
"""
MOLT - Recursive Self-Improvement Engine
Tree Growth Interface Edition
"""

import sys
import json
import time
from pathlib import Path
from core.iterate import MoltIterator
from core.ollama_bridge import OllamaClient
from ui.render import TreeRenderer
from memory.improvements import ImprovementMemory

class Molt:
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.config = self._load_config()
        self.ollama = OllamaClient(
            host=self.config.get('ollama_host', 'http://127.0.0.1:11434'),
            model=self.config.get('model', 'deepseek-r1:1.5b')
        )
        self.iterator = MoltIterator(self.ollama)
        self.memory = ImprovementMemory(self.base_path / 'memory')
        self.renderer = TreeRenderer()
        
    def _load_config(self):
        config_path = self.base_path / 'config.json'
        if config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}
    
    def run(self, task: str, max_iterations: int = 5):
        """Run molt on a task with tree visualization"""
        self.renderer.clear()
        self.renderer.plant_seed(task)
        
        results = []
        for i in range(max_iterations):
            self.renderer.show_growth_ring(i + 1)
            
            # Iterate
            result = self.iterator.iterate(task, results)
            results.append(result)
            
            # Visualize as branches
            self.renderer.grow_branch(
                iteration=i + 1,
                content=result['output'][:100],  # Preview
                score=result.get('score', 0)
            )
            
            # Store if it's an improvement
            if result.get('is_improvement', False):
                self.memory.store(task, result)
                self.renderer.bloom_leaf(i + 1)
            
            time.sleep(0.5)  # Dramatic effect
        
        self.renderer.show_canopy()
        return self.memory.get_best(task)

def main():
    if len(sys.argv) < 2:
        print("Usage: python molt.py 'your task here'")
        print("Example: python molt.py 'write a function to calculate fibonacci'")
        sys.exit(1)
    
    task = ' '.join(sys.argv[1:])
    molt = Molt()
    
    print("\n🌱 MOLT: Recursive Growth System")
    print("━" * 50)
    
    try:
        best = molt.run(task)
    except ConnectionError as e:
        print(f"\n❌ Connection Error: {e}")
        print("Please ensure Ollama is running (`ollama serve`) and accessible.")
        sys.exit(1)
    
    if not best:
        print("\n" + "━" * 50)
        print("🥀 No improvements were generated. Halting growth.")
        sys.exit(0)
    
    print("\n" + "━" * 50)
    print("🌳 FINAL GROWTH:")
    print(best['output'])
    print(f"\n📊 Final Score: {best.get('score', 0):.2f}")

if __name__ == '__main__':
    main()
