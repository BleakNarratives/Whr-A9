import unittest
import tempfile
import os
from src.core.scanners.complexity_scanner import ComplexityScanner
from src.core.loom.models import MetricType

class TestComplexityScanner(unittest.TestCase):
    def test_scan(self):
        scanner = ComplexityScanner()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def simple():
    return 1

def complex(x):
    if x > 0:
        for i in range(x):
            print(i)
    else:
        while x < 0:
            x += 1
    try:
        x / 0
    except ZeroDivisionError:
        pass
""")
            filename = f.name
        
        try:
            weave = scanner.scan(filename)
            
            # Check results
            self.assertIn("simple", weave.lexemes)
            self.assertIn("complex", weave.lexemes)
            
            # Check complexity
            def get_comp(lexeme):
                for m in lexeme.metrics:
                    if m.metric_type == MetricType.COMPLEXITY:
                        return m.value
                return 0
            
            self.assertEqual(get_comp(weave.lexemes["simple"]), 1.0)
            self.assertEqual(get_comp(weave.lexemes["complex"]), 6.0)
            
        finally:
            os.remove(filename)

if __name__ == '__main__':
    unittest.main()
