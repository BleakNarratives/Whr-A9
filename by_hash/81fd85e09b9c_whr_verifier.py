import ast
import os

# Forbidden modules and functions
FORBIDDEN_MODULES = {'os', 'subprocess', 'shutil', 'socket', 'sys'}
FORBIDDEN_FUNCTIONS = {'eval', 'exec', 'compile', 'open'}

class WhorlVerifier:
    def __init__(self, allowed_root):
        self.allowed_root = allowed_root

    def verify(self, code_string):
        """
        Hardened static analysis for WHORL runtime.
        """
        try:
            tree = ast.parse(code_string)
        except SyntaxError as e:
            return False, f"Syntax Error: {e}"

        for node in ast.walk(tree):
            # 1. Block forbidden imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Simplified import checking
                for name in (node.names if isinstance(node, ast.Import) else [ast.Name(id=node.module)]):
                    if getattr(name, 'name', name.id) in FORBIDDEN_MODULES:
                        return False, f"Security Violation: Forbidden import {getattr(name, 'name', name.id)}"

            # 2. Block forbidden function calls
            if isinstance(node, ast.Call):
                # Direct call check (eval(), exec())
                if isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_FUNCTIONS:
                    return False, f"Security Violation: Forbidden call {node.func.id}"
                
                # Attribute call check (os.system(), subprocess.run())
                if isinstance(node.func, ast.Attribute):
                    obj = self._get_attr_obj(node.func)
                    if obj in FORBIDDEN_MODULES:
                        return False, f"Security Violation: Forbidden call {obj}.{node.func.attr}"

            # 3. Block file operations outside root (partial check)
            if isinstance(node, ast.Call) and getattr(getattr(node, 'func', None), 'id', None) == 'open':
                return False, "Security Violation: open() is forbidden."

        return True, "Code hardened and verified."

    def _get_attr_obj(self, node):
        if isinstance(node.value, ast.Name):
            return node.value.id
        elif isinstance(node.value, ast.Attribute):
            return self._get_attr_obj(node.value)
        return None
