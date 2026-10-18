import ast
import tokenize
from ..loom.models import Lexeme, LoomMetric, LoomWeave, MetricType

class ScribeScanner:
    """SMACK-grade scanner to quantify the semantic documentation density."""

    def scan(self, file_path: str) -> LoomWeave:
        """Analyze the file, assess its semantic documentation, and return the Vibe."""
        # 1. Parse AST to locate functions and docstrings
        with open(file_path, 'r') as f:
            source = f.read()
            tree = ast.parse(source)

        # 2. Tokenize to map comment line numbers (high-precision)
        comment_lines = set()
        with open(file_path, 'rb') as f:
            for tok_type, _, start, _, _ in tokenize.tokenize(f.readline):
                if tok_type == tokenize.COMMENT:
                    comment_lines.add(start[0])

        # 3. Analyze functions: Total vs Documented
        total_funcs = 0
        documented_funcs = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_funcs += 1
                has_docstring = ast.get_docstring(node) is not None
                # Check for comment on the same or preceding line
                has_comment = (node.lineno in comment_lines or (node.lineno - 1) in comment_lines)
                
                if has_docstring or has_comment:
                    documented_funcs += 1

        # 4. Calculate SMACK score
        score = (documented_funcs / total_funcs) if total_funcs > 0 else 1.0

        # 5. Create SMACK Lexeme for the file
        file_lexeme = Lexeme(
            id=file_path,
            label=f"file:{file_path}"
        )
        file_lexeme.add_metric(LoomMetric(
            name="semantic_vibe",
            value=float(score),
            metric_type=MetricType.VIBE
        ))

        weave = LoomWeave(version="1.0")
        weave.add_lexeme(file_lexeme)
        
        return weave
