import ast
from ..loom.models import Lexeme, LoomMetric, LoomWeave, MetricType

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.complexity = 1
    
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def visit_Try(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.complexity += 1
        self.generic_visit(node)

class ComplexityScanner:
    def scan(self, file_path: str) -> LoomWeave:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
        
        weave = LoomWeave(version="1.0")
        
        # Find all functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                visitor = ComplexityVisitor()
                # Visit the function body
                for item in node.body:
                    visitor.visit(item)
                
                complexity = visitor.complexity
                
                # Create Lexeme for function
                lexeme = Lexeme(
                    id=node.name,
                    label=f"function:{node.name}"
                )
                lexeme.add_metric(LoomMetric(
                    name="cyclomatic_complexity",
                    value=float(complexity),
                    metric_type=MetricType.COMPLEXITY
                ))
                
                weave.add_lexeme(lexeme)
        
        return weave
