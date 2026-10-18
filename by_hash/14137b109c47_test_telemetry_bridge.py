import unittest
import tempfile
import os
from src.api.telemetry_bridge import TelemetryBridge
from src.core.scanners.complexity_scanner import ComplexityScanner
from src.core.scanners.scribe_scanner import ScribeScanner
from src.core.loom.models import MetricType

class TestTelemetryBridge(unittest.TestCase):
    def test_aggregate(self):
        bridge = TelemetryBridge()
        bridge.register_scanner(ComplexityScanner())
        bridge.register_scanner(ScribeScanner())
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def documented():
    \"\"\"Docstring.\"\"\"
    if True:
        pass
    return 1
""")
            filename = f.name
        
        try:
            unified_weave = bridge.aggregate(filename)
            
            # Verify aggregation
            self.assertIn("documented", unified_weave.lexemes)
            self.assertIn(filename, unified_weave.lexemes)
            
            # Check metrics for function lexeme (from ComplexityScanner)
            func_lexeme = unified_weave.lexemes["documented"]
            comp_metric = next((m for m in func_lexeme.metrics if m.metric_type == MetricType.COMPLEXITY), None)
            self.assertIsNotNone(comp_metric)
            self.assertEqual(comp_metric.value, 2.0)
            
            # Check metrics for file lexeme (from ScribeScanner)
            file_lexeme = unified_weave.lexemes[filename]
            vibe_metric = next((m for m in file_lexeme.metrics if m.metric_type == MetricType.VIBE), None)
            self.assertIsNotNone(vibe_metric)
            self.assertEqual(vibe_metric.value, 1.0)
            
        finally:
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
