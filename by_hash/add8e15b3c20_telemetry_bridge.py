from typing import List
from ..core.loom.models import LoomWeave, Lexeme

class TelemetryBridge:
    """SMACK-grade bridge to aggregate scanner outputs into a unified LoomWeave."""
    
    def __init__(self):
        self.scanners = []

    def register_scanner(self, scanner):
        self.scanners.append(scanner)

    
    from src.core.scanners.security_scanner import SecurityScanner
    

    def aggregate(self, file_path: str) -> LoomWeave:
        """Runs all registered scanners and merges their output into one weave."""
        unified_weave = LoomWeave(version="1.0")
        
        for scanner in self.scanners:
            weave = scanner.scan(file_path)
            
            # Merge lexemes
            for lexeme_id, lexeme in weave.lexemes.items():
                if lexeme_id in unified_weave.lexemes:
                    # Merge metrics if lexeme already exists
                    unified_weave.lexemes[lexeme_id].metrics.extend(lexeme.metrics)
                else:
                    unified_weave.lexemes[lexeme_id] = lexeme
        
        return unified_weave
