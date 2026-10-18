import unittest
import tempfile
import os
from src.core.scanners.scribe_scanner import ScribeScanner
from src.core.loom.models import MetricType

class TestScribeScanner(unittest.TestCase):
    def test_scan(self):
        scanner = ScribeScanner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def documented():
    \"\"\"This function is documented.\"\"\"
    return 1

# This function is also documented via comment
def commented():
    return 2

def undocumented():
    return 3
""")
            filename = f.name
        
        try:
            weave = scanner.scan(filename)
            
            # File-level lexeme should exist
            self.assertIn(filename, weave.lexemes)
            file_lexeme = weave.lexemes[filename]
            
            # Get VIBE metric
            vibe_metric = next(
                (m for m in file_lexeme.metrics if m.metric_type == MetricType.VIBE), 
                None
            )
            self.assertIsNotNone(vibe_metric)
            
            # 2/3 documented
            self.assertAlmostEqual(vibe_metric.value, 2.0/3.0)
            
        finally:
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
