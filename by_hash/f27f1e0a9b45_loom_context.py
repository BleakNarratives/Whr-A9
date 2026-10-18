import os
from src.api.telemetry_bridge import TelemetryBridge
from src.core.scanners.complexity_scanner import ComplexityScanner
from src.core.scanners.scribe_scanner import ScribeScanner
from src.core.scanners.security_scanner import SecurityScanner

class LoomContext:
    """The unified fabric where UI, API, and Core fold into one."""
    def __init__(self):
        self.bridge = TelemetryBridge()
        self.bridge.register_scanner(ComplexityScanner())
        self.bridge.register_scanner(ScribeScanner())
        self.bridge.register_scanner(SecurityScanner())

    def interact_and_traverse(self, node_id: str):
        """Fold navigation into execution: navigate and trigger semantic analysis."""
        print(f"[*] Folding interaction for: {node_id}")
        
        # In a real implementation, this would map node_id to a real file path
        # Here we simulate the inseparability by triggering a deep scan
        # on the requested target, effectively making the UI request
        # part of the execution loop.
        target = f"CodeCity-Bench/src/core/scanners/{node_id.replace('-', '_')}.py"
        if not os.path.exists(target):
            target = "CodeCity-Bench/src/core/scanners/scribe_scanner.py"
        
        weave = self.bridge.aggregate(target)
        return f"Folded navigation: {node_id}. Semantics indexed: {len(weave.lexemes)}."

# Global context to blur boundaries
context = LoomContext()
