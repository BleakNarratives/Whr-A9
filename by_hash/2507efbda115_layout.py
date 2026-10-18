import math

def calculate_layout(nodes_data):
    nodes = {}
    for node_id, data in nodes_data.items():
        nodes[node_id] = {
            'connections': data.get('connections', []),
            'complexity': data.get('complexity', 0.0),
            'x': 0.0, 'y': 0.0, 'z': 0.0
        }

    # Initialize positions randomly (simplified)
    for node_id in nodes:
        nodes[node_id]['x'] = (hash(node_id) % 1000) / 100.0 - 5
        nodes[node_id]['y'] = (hash(node_id + 'y') % 1000) / 100.0 - 5

    iterations = 50
    k = 10.0 # Optimal distance
    dt = 0.1 # Time step

    for _ in range(iterations):
        forces = {node_id: {'x': 0.0, 'y': 0.0} for node_id in nodes}
        
        # Calculate repulsion forces
        for id1 in nodes:
            for id2 in nodes:
                if id1 == id2: continue
                dx = nodes[id1]['x'] - nodes[id2]['x']
                dy = nodes[id1]['y'] - nodes[id2]['y']
                dist_sq = dx*dx + dy*dy
                dist = math.sqrt(dist_sq)
                if dist == 0: dist = 0.01 # Avoid division by zero
                
                fx = (dx / dist) * (k*k / dist) if dist > 0 else (k*k / 0.01)
                fy = (dy / dist) * (k*k / dist) if dist > 0 else (k*k / 0.01)
                forces[id1]['x'] += fx
                forces[id1]['y'] += fy
                forces[id2]['x'] -= fx
                forces[id2]['y'] -= fy
        
        # Calculate attraction forces
        for id1 in nodes:
            for conn_id in nodes[id1]['connections']:
                if conn_id in nodes:
                    dx = nodes[id1]['x'] - nodes[conn_id]['x']
                    dy = nodes[id1]['y'] - nodes[conn_id]['y']
                    dist = math.sqrt(dx*dx + dy*dy)
                    if dist == 0: dist = 0.01
                    
                    fx = (dx / dist) * (dist*dist / k) if dist > 0 else (dist*dist / k)
                    fy = (dy / dist) * (dist*dist / k) if dist > 0 else (dist*dist / k)
                    forces[id1]['x'] -= fx
                    forces[id1]['y'] -= fy
                    forces[conn_id]['x'] += fx
                    forces[conn_id]['y'] += fy

        # Update positions
        for node_id in nodes:
            nodes[node_id]['x'] += forces[node_id]['x'] * dt
            nodes[node_id]['y'] += forces[node_id]['y'] * dt

    # Calculate Z coordinate from normalized complexity
    complexities = [n['complexity'] for n in nodes.values()]
    max_comp = max(complexities) if complexities else 1.0
    min_comp = min(complexities) if complexities else 0.0
    
    for node_id in nodes:
        if max_comp == min_comp:
            nodes[node_id]['z'] = 0.5 # Neutral Z if all complexities are the same
        else:
            nodes[node_id]['z'] = (nodes[node_id]['complexity'] - min_comp) / (max_comp - min_comp)

    # Format output
    results = {}
    for node_id, data in nodes.items():
        results[node_id] = {'x': data['x'], 'y': data['y'], 'z': data['z']}
    return results
