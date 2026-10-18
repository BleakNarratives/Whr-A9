from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

class MetricType(Enum):
    STRUCTURAL = "structural"
    COMPLEXITY = "complexity"
    SEMANTIC = "semantic"
    VIBE = "vibe"
    TOPOLOGICAL = "topological"
    SECURITY = "security"

@dataclass(frozen=True)
class LoomMetric:
    """A single data point within the Loom topological space."""
    name: str
    value: float
    metric_type: MetricType
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Lexeme:
    """
    The fundamental unit of the 'Loom' weave. 
    A Lexeme represents a discrete 'knot' of information in the code topology.
    """
    id: str
    label: str  # e.g., "class:User", "function:calculate_total"
    metrics: List[LoomMetric] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)  # IDs of connected Lexemes (the 'weave')
    coordinates: Optional[Dict[str, float]] = None  # 3D position (x, y, z) in the topological space
    
    def add_metric(self, metric: LoomMetric):
        self.metrics.append(metric)

    def connect_to(self, other_lexeme_id: str):
        if other_lexeme_id not in self.connections:
            self.connections.append(other_lexeme_id)

@dataclass
class LoomWeave:
    """
    The complete topological representation of a codebase.
    A Weave is a collection of Lexemes and their connections.
    """
    version: str
    lexemes: Dict[str, Lexeme] = field(default_factory=dict)
    topology_signature: str = ""  # A hash representing the current 'shape' of the weave

    def add_lexeme(self, lexeme: Lexeme):
        self.lexemes[lexeme.id] = lexeme

    def get_connections(self, lexeme_id: str) -> List[Lexeme]:
        lexeme = self.lexemes.get(lexeme_id)
        if not lexeme:
            return []
        return [self.lexemes[conn_id] for conn_id in lexeme.connections if conn_id in self.lexemes]
