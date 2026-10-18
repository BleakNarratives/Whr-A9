#!/usr/bin/env python3
"""
MOLT - Recursive Self-Improvement Engine
Core iteration logic with Headless Mode support.
Path: /data/data/com.termux/files/home/MoltBleak/molt.py
"""

import sys
import json
import time
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).parent
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

try:
    from src.core.iterate import MoltIterator
    from src.core.ollama_bridge import OllamaClient
    from src.ui.render import TreeRenderer
    from src.memory.improvements import ImprovementMemory
except ImportError as e:
    print(f"Error importing Molt modules: {e}")
    sys.exit(1)

class Molt:
    def __init__(self):
        self.base_path = Path(__file__).parent 
        self.config = self._load_config()
        self.ollama = OllamaClient(
            host=self.config.get('ollama_host', 'http://127.0.0.1:11434'),
            model=self.config.get('model', 'deepseek-r1:1.5b')
        )
        self.iterator = MoltIterator(self.ollama)
        self.memory = ImprovementMemory(self.base_path / 'src/memory') 
        self.renderer = TreeRenderer()

    def _load_config(self):
        config_path = self.base_path / 'src/config/config.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {'ollama_host': 'http://127.0.0.1:11434', 'model': 'deepseek-r1:1.5b', 'default_iterations': 5}
    
    def run(self, task: str, max_iterations: Optional[int] = None, headless: bool = False) -> Dict:
        if max_iterations is None:
            max_iterations = self.config.get('default_iterations', 5) 

        if not headless:
            self.renderer.clear()
            self.renderer.plant_seed(task)
        
        results = []
        for i in range(max_iterations):
            iteration_result = self.iterator.iterate(task, results)
            results.append(iteration_result)

            if 'error' in iteration_result:
                return iteration_result
            
            if not headless:
                self.renderer.grow_branch(iteration=i + 1, content=iteration_result.get('output', '')[:100], score=iteration_result.get('score', 0))
            
            if iteration_result.get('is_improvement', False):
                self.memory.store(task, iteration_result)
            
            time.sleep(0.1) 
        
        final_best = self.memory.get_best(task)
        return final_best if final_best else results[-1]

def main():
    parser = argparse.ArgumentParser(description="MOLT Engine")
    parser.add_argument('task', nargs='?', help='The task to perform')
    parser.add_argument('--headless', action='store_true', help='Run without UI visualization')
    parser.add_argument('--iterations', type=int, help='Override max iterations')
    args = parser.parse_args()

    if not args.task:
        print("Usage: python molt.py 'your task' [--headless] [--iterations N]")
        sys.exit(1)
    
    molt_engine = Molt()
    
    if args.headless:
        # Structured output for headless mode
        result = molt_engine.run(args.task, max_iterations=args.iterations, headless=True)
        print(json.dumps(result))
    else:
        print("\n🌱 MOLT: Recursive Growth System")
        best_result = molt_engine.run(args.task, max_iterations=args.iterations)
        print("\n🌳 FINAL GROWTH RESULT:")
        print(best_result.get('output', 'No output generated.'))

if __name__ == '__main__':
    main()
