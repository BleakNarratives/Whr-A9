import ast
import os
from ..loom.models import Lexeme, LoomMetric, LoomWeave, MetricType

class SecurityScanner:
    """Detects common security vulnerabilities in Python code."""

    DANGEROUS_FUNCS = {"eval", "exec", "compile", "__import__"}
    DANGEROUS_ATTRS = {"shell": "subprocess.run with shell=True", "pickle": "pickle.loads"}

    def scan(self, file_path: str) -> LoomWeave:
        content = self._read(file_path)
        if not content:
            return LoomWeave(version="1.0")
        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            return LoomWeave(version="1.0")
        weave = LoomWeave(version="1.0")
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    if node.func.id in self.DANGEROUS_FUNCS:
                        self._flag(weave, file_path, node.lineno, node.func.id + '()')
                elif isinstance(node.func, ast.Attribute):
                    if node.func.attr == "run":
                        for kw in node.keywords:
                            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value:
                                self._flag(weave, file_path, node.lineno, "subprocess.run with shell=True")
                    elif node.func.attr == "loads" and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "pickle":
                            self._flag(weave, file_path, node.lineno, "pickle.loads()")
        return weave

    def _read(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception:
            return ""

    def _flag(self, weave, path, lineno, issue):
        lid = f"{os.path.basename(path)}:L{lineno}:{issue.replace(' ','_')}"
        lex = Lexeme(id=lid, label=f"SECURITY: {issue}")
        lex.add_metric(LoomMetric(name="severity", value=1.0, metric_type=MetricType.SECURITY))
        weave.add_lexeme(lex)
