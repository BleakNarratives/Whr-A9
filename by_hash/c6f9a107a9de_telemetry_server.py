import json
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.api.loom_context import context

# Simple TOML parser (no external libs)
def parse_toml(file_path):
    config = {}
    current_section = config
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'): continue
            if line.startswith('[') and line.endswith(']'):
                section = line[1:-1]
                config[section] = {}
                current_section = config[section]
            elif '=' in line:
                key, val = line.split('=', 1)
                current_section[key.strip()] = val.strip().replace('"', '')
    return config

class TelemetryHandler(BaseHTTPRequestHandler):
    # Derive config path relative to this script: src/api/telemetry_server.py -> ../../visualizer_config.toml
    _this_dir = os.path.dirname(os.path.abspath(__file__))
    _project_root = os.path.dirname(os.path.dirname(_this_dir))
    config = parse_toml(os.path.join(_project_root, "visualizer_config.toml"))
    bridge = TelemetryBridge()
        # Dynamically check endpoints
        endpoint = self.config.get('visualizer', {}).get('default', {}).get('endpoint', '/api/topology')

        if self.path.startswith(endpoint):
            # For simplicity, aggregate a fixed scanner file
            file_path = "CodeCity-Bench/src/core/scanners/scribe_scanner.py" 
            weave = context.bridge.aggregate(file_path)

            data = {
                "lexemes": {k: {"label": v.label, "metrics": [{"name": m.name, "value": m.value} for m in v.metrics]} for k, v in weave.lexemes.items()}
            }

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))

        elif self.path.startswith('/api/interact'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            node_id = params.get('id', [None])[0]

            # The Folding: interaction triggers execution via context
            message = context.interact_and_traverse(node_id)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"message": message}).encode('utf-8'))
        else:
            self.send_error(404)

def run_server(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TelemetryHandler)
    print(f"[*] Telemetry Server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
