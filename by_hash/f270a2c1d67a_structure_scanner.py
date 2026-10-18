import os
from typing import Dict, Any
from .base import BaseScanner
from ..loom.models import LoomWeave, Lexeme, LoomMetric, MetricType

class CodeStructureScanner(BaseScanner):
    """
    A scanner that maps the file system hierarchy into a LoomWeave.
    Each file and directory becomes a Lexeme.
    """

    def scan(self) -> LoomWeave:
        weave = LoomWeave(version="1.0")
        
        for root, dirs, files in os.walk(self.target_path):
            # Handle directories
            for d in dirs:
                dir_path = os.path.join(root, d)
                rel_path = os.path.relpath(dir_path, self.target_path)
                
                lexeme_id = f"dir:{rel_path}"
                lexeme = Lexeme(id=lexeme_id, label=f"Directory: {rel_path}")
                
                # Add structural metric: depth
                depth = rel_path.count(os.sep)
                lexeme.add_metric(LoomMetric(
                    name="depth",
                    value=float(depth),
                    metric_type=MetricType.STRUCTURAL,
                    metadata={"type": "directory"}
                ))
                
                weave.add_lexeme(lexeme)

            # Handle files
            for f in files:
                file_path = os.path.join(root, f)
                rel_path = os.path.relpath(file_path, self.target_path)
                
                lexeme_id = f"file:{rel_path}"
                lexeme = Lexeme(id=lexeme_id, label=f"File: {rel_path}")
                
                # Add structural metric: size
                size = os.path.getsize(file_path)
                lexeme.add_metric(LoomMetric(
                    name="size",
                    value=float(size),
                    metric_type=MetricType.STRUCTURAL,
                    metadata={"type": "file"}
                ))
                
                weave.add_lexeme(lexeme)
                
                # Basic connection: files are "contained" in their parent directory
                parent_dir = os.path.dirname(rel_path)
                if parent_dir:
                    parent_lexeme_id = f"dir:{parent_dir}"
                    lexeme.connect_to(parent_lexeme_id)
                elif rel_path != ".": # Root files connect to nothing special or a root lexeme
                    pass

        return weave

    def get_summary(self) -> Dict[str, Any]:
        # This is a placeholder. In a real implementation, 
        # it would return actual statistics from the scan.
        return {
            "status": "success",
            "target": self.target_path,
            "message": "File system hierarchy mapped to LoomWeave."
        }

if __name__ == "__main__":
    # Quick test of the scanner
    # Using the current directory for testing
    test_path = os.getcwd()
    scanner = CodeStructureScanner(test_path)
    weave = scanner.scan()
    
    print(f"Scanned {len(weave.lexemes)} Lexemes.")
    
    # Print first 5 lexemes
    count = 0
    for lexeme in weave.lexemes.values():
        print(f"- {lexeme.label} (Metrics: {len(lexeme.metrics)})")
        count += 1
        if count >= 5:
            break
