class LOUGH_FEP:
    """
    Legacy Overlay Unified Graphics Hub
    + Field Excited Programming Runtime
    """
    
    def __init__(self, janebox_instance):
        """Bind to shared state"""
        
    # --- LOUGH Methods ---
    def render_whorl_to_svg(self, whorl_graph, overlay_type="spatial"):
        """Convert Whorl graph to SVG via force-directed layout"""
        
    def geo_overlay(self, whorl_graph, lat, lng, zoom=14):
        """Fetch Maps tile, composite Whorl nodes onto it"""
        
    def camelot_overlay(self, whorl_graph, key="Cmin"):
        """Map Whorl tension edges to Camelot wheel positions"""
        
    # --- FEP Methods ---
    def excite_field(self, signal_pattern, field_graph):
        """Propagate signal through field, return collapse path"""
        
    def define_trap(self, capability_level, challenge_fn):
        """Register a trap function for capability gating"""
        
    def query_with_trap(self, query, claimed_capability):
        """Model queries FEP field, trap gates capability"""
        
    # --- CEP Methods ---
    def attention_cascade(self, whorl_key, agent_id):
        """Mark whorl as touched, increment heat score"""
        
    def detect_drift(self, agent_output, sediment_history):
        """Flag outputs diverging from sediment pattern"""
        
    def emergence_score(self, swarm_outputs, individual_baselines):
        """Quantify swarm vs individual performance delta"""
