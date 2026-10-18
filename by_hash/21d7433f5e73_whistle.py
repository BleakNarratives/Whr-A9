import sys
import os

def whistle(mode="topology"):
    """A secret whistle to navigate the Loom."""
    print(f"✨ Whistling for {mode}... 🎶")
    
    # Map modes to file paths
    viz_files = {
        "topology": "CodeCity-Bench/src/visualizers/topology.html",
        "apocalypse": "CodeCity-Bench/src/visualizers/apocalypse.html"
    }
    
    viz_path = os.path.abspath(viz_files.get(mode, viz_files["topology"]))
    
    print(f"[*] Opening RootBase Visualizer [{mode}]: {viz_path}")
    
    if sys.platform == 'linux' and 'TERMUX_VERSION' in os.environ:
        os.system(f"termux-open '{viz_path}'")
    else:
        print(f"File available at: {viz_path}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "topology"
    whistle(mode)
