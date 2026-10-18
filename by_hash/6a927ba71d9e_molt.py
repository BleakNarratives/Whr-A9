#!/usr/bin/env python3
"""
MOLT - Recursive Self-Improvement Engine
Core iteration logic.
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

# --- Dynamically adjust sys.path to import from the correct location ---
# Determine the base directory of the script (project root)
BASE_DIR = Path(__file__).parent

# Add src directory to sys.path to allow absolute imports from src.module
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

try:
    # Import core Molt classes from their respective locations within src
    from src.core.iterate import MoltIterator
    from src.core.ollama_bridge import OllamaClient
    from src.ui.render import TreeRenderer
    from src.memory.improvements import ImprovementMemory
    # Assuming a config loader exists in src.config
except ImportError as e:
    print(f"Error importing Molt modules: {e}")
    print("Please ensure the 'src' directory structure and __init__.py files are correctly set up")
    print("and that your Python environment has necessary dependencies installed.")
    sys.exit(1)

class Molt:
    def __init__(self):
        # Base path is the root directory where molt.py is located
        self.base_path = Path(__file__).parent 
        self.config = self._load_config()
        
        # OllamaClient initialization uses config values
        self.ollama = OllamaClient(
            host=self.config.get('ollama_host', 'http://127.0.0.1:11434'),
            model=self.config.get('model', 'deepseek-r1:1.5b')
        )
        self.iterator = MoltIterator(self.ollama)
        # Memory initialization path adjusted to reflect new structure within src
        self.memory = ImprovementMemory(self.base_path / 'src/memory') 
        self.renderer = TreeRenderer() # Internal visualization

    def _load_config(self):
        # Load config from src/config
        config_path = self.base_path / 'src/config/config.json'
        if config_path.exists():
            try:
                with open(config_path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {config_path}. Using defaults.")
                return {}
        
        # Fallback or default config if file not found
        print(f"Warning: Config file not found at {config_path}. Using defaults.")
        return {
            'ollama_host': 'http://127.0.0.1:11434',
            'model': 'deepseek-r1:1.5b',
            'default_iterations': 5 # Example default
        }
    
    def run(self, task: str, max_iterations: Optional[int] = None) -> Dict:
        """Run molt on a task with tree visualization (internal) and return best result."""
        if max_iterations is None:
            # Use default from config if not provided
            max_iterations = self.config.get('default_iterations', 5) 

        self.renderer.clear()
        self.renderer.plant_seed(task)
        
        results = []
        for i in range(max_iterations):
            self.renderer.show_growth_ring(i + 1)
            
            # Iterate and get result from MoltIterator
            iteration_result = self.iterator.iterate(task, results)
            results.append(iteration_result) # Always append the result, even if it's an error

            # Check for error propagated from MoltIterator
            if 'error' in iteration_result:
                print(f"Iteration {i+1} encountered an error: {iteration_result['error']}")
                self.renderer.show_error(f"Error in iteration {i+1}: {iteration_result['error']}")
                # Optionally, stop iterations on first error or continue
                # For now, we will stop and return the last result which contains the error
                return iteration_result
            
            # Visualize as branches
            self.renderer.grow_branch(
                iteration=i + 1,
                content=iteration_result.get('output', '')[:100],  # Preview
                score=iteration_result.get('score', 0)
            )
            
            # Store if it's an improvement
            if iteration_result.get('is_improvement', False):
                self.memory.store(task, iteration_result)
                self.renderer.bloom_leaf(i + 1)
            
            time.sleep(0.1) 
        
        self.renderer.show_canopy() 

        # Return the best result found, or the last error if it occurred after some iterations
        final_best = self.memory.get_best(task)
        if final_best:
            return final_best
        elif results and 'error' in results[-1]:
            return results[-1] # Return the last error if no improvement was found
        else:
            return {'output': 'No successful iterations or improvements found.', 'score': 0.0}


def main():
    if len(sys.argv) < 2:
        print("Usage: python molt.py 'your task here'")
        print("Example: python molt.py 'write a function to calculate fibonacci'")
        sys.exit(1)
    
    task = ' '.join(sys.argv[1:])
    molt_engine = Molt()
    
    print("\n🌱 MOLT: Recursive Growth System (CORE ENGINE)")
    print("━" * 50)
    
    best_result = molt_engine.run(task)
    
    print("\n" + "━" * 50)
    print("🌳 FINAL GROWTH RESULT:")
    if 'error' in best_result:
        print(f"❌ An error prevented successful completion: {best_result['error']}")
    else:
        print(best_result.get('output', 'No output generated.'))
        print(f"\n📊 Final Score: {best_result.get('score', 0):.2f}")

if __name__ == '__main__':
    main()
