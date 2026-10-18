"""
Improvement Memory - Store what works
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ImprovementMemory:
    def __init__(self, memory_path: Path):
        self.memory_path = Path(memory_path)
        self.memory_path.mkdir(parents=True, exist_ok=True)
        self.db_path = self.memory_path / 'improvements.json'
        self.db = self._load_db()
        
    def _load_db(self) -> Dict:
        """Load improvement database"""
        if self.db_path.exists():
            try:
                with open(self.db_path) as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_db(self):
        """Save improvement database"""
        with open(self.db_path, 'w') as f:
            json.dump(self.db, f, indent=2)
    
    def store(self, task: str, result: Dict):
        """Store an improvement"""
        task_key = self._task_key(task)
        
        if task_key not in self.db:
            self.db[task_key] = {
                'task': task,
                'history': []
            }
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'output': result['output'],
            'score': result.get('score', 0),
            'iteration': result.get('iteration', 0)
        }
        
        self.db[task_key]['history'].append(entry)
        self._save_db()
    
    def get_best(self, task: str) -> Optional[Dict]:
        """Get best result for a task"""
        task_key = self._task_key(task)
        
        if task_key not in self.db:
            return None
        
        history = self.db[task_key]['history']
        if not history:
            return None
        
        # Return highest scoring result
        return max(history, key=lambda x: x.get('score', 0))
    
    def get_history(self, task: str) -> List[Dict]:
        """Get full history for a task"""
        task_key = self._task_key(task)
        return self.db.get(task_key, {}).get('history', [])
    
    def _task_key(self, task: str) -> str:
        """Generate key from task"""
        # Simple hash for now
        return str(hash(task.lower().strip()))
    
    def list_tasks(self) -> List[str]:
        """List all stored tasks"""
        return [v['task'] for v in self.db.values()]
    
    def export_best(self, output_dir: Path):
        """Export all best results to files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for task_key, data in self.db.items():
            best = max(data['history'], key=lambda x: x.get('score', 0))
            filename = f"best_{task_key[:8]}.txt"
            filepath = output_dir / filename
            
            with open(filepath, 'w') as f:
                f.write(f"Task: {data['task']}\n")
                f.write(f"Score: {best['score']:.2f}\n")
                f.write(f"Date: {best['timestamp']}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(best['output'])
