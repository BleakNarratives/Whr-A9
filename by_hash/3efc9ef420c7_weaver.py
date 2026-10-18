from .layout import calculate_layout
from .models import Lexeme, LoomMetric, LoomWeave, MetricType

class LoomWeaver:
    """
    The LoomWeaver is responsible for transforming discrete code metrics
    into a continuous topological surface (the 'Weave').
    """

    def __init__(self, weave: LoomWeave):
        self.weave = weave

    def weave_topology(self):
        """
        Calculates 3D coordinates for all Lexemes based on their
        interconnectedness and metric values using a force-directed layout.
        """
        nodes_data = {}
        for lexeme_id, lexeme in self.weave.lexemes.items():
            complexity_metric = 0.0
            for metric in lexeme.metrics:
                if metric.metric_type == MetricType.COMPLEXITY:
                    complexity_metric = metric.value
                    break # Assuming only one complexity metric per lexeme
            
            nodes_data[lexeme_id] = {
                'connections': lexeme.connections,
                'complexity': complexity_metric
            }

        # Calculate layout using the force-directed algorithm
        calculated_coordinates = calculate_layout(nodes_data)

        # Assign the calculated coordinates back to the Lexeme objects
        for lexeme_id, coords in calculated_coordinates.items():
            if lexeme_id in self.weave.lexemes:
                self.weave.lexemes[lexeme_id].coordinates = coords

        # Update the weave signature (optional, but good practice)
        self.weave.topology_signature = self.calculate_weave_signature()

    def calculate_weave_signature(self) -> str:
        """
        Generates a 'topology signature' based on the current state of the weave.
        """
        # This is a placeholder for a signature calculation based on
        # the weave's structural properties.
        return f"weave-v1-{len(self.weave.lexemes)}"

def ignite_loom_magic():
    """A secret spell to ignite the Loom."""
    print("✨ The Loom is crackling with ancient, forbidden energy! ✨")

if __name__ == "__main__":
    # Quick test of the weaver
    weave = LoomWeave(version="1.0")
    
    # Create Lexemes with complexity metrics
    l1 = Lexeme(id="1", label="node_1")
    l1.add_metric(LoomMetric(name="complexity", value=0.3, metric_type=MetricType.COMPLEXITY))
    
    l2 = Lexeme(id="2", label="node_2")
    l2.add_metric(LoomMetric(name="complexity", value=0.7, metric_type=MetricType.COMPLEXITY))
    
    l1.connect_to("2")
    l2.connect_to("1")
    
    weave.add_lexeme(l1)
    weave.add_lexeme(l2)
    
    weaver = LoomWeaver(weave)
    
    # Calculate topology (this will now use the layout algorithm)
    weaver.weave_topology()
    
    print(f"Weave Signature: {weaver.calculate_weave_signature()}")
    print(f"Node 1 Coords: {l1.coordinates}")
    print(f"Node 2 Coords: {l2.coordinates}")
