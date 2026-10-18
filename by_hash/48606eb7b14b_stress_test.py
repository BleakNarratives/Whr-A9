import os
import tempfile
from src.api.telemetry_bridge import TelemetryBridge
from src.core.scanners.complexity_scanner import ComplexityScanner
from src.core.scanners.scribe_scanner import ScribeScanner

def run_stress_test():
    bridge = TelemetryBridge()
    bridge.register_scanner(ComplexityScanner())
    bridge.register_scanner(ScribeScanner())
    
    print("Starting stress test...")
    files = []
    try:
        for i in range(20):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(f"def func_{i}():\n    if True:\n        pass\n    return {i}")
                files.append(f.name)
        
        for file in files:
            bridge.aggregate(file)
            
        print(f"Successfully processed {len(files)} files.")
        
    finally:
        for file in files:
            if os.path.exists(file):
                os.remove(file)
    print("Stress test completed.")

if __name__ == "__main__":
    run_stress_test()
