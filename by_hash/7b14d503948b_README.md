# CodeCity-Bench

A professional-grade workbench for code analysis, topology visualization, and telemetry-driven exploration.

## Advanced Features
- **Loom Engine:** Force-directed topological graph layout algorithm.
- **Scanners:** 
  - `ComplexityScanner`: AST-based cyclomatic complexity analysis.
  - `ScribeScanner`: Documentation density ("Vibe") analysis.
- **Telemetry Bridge:** Aggregation of scanner metrics into a unified `LoomWeave`.
- **Backend:** `TelemetryServer` (API) with dynamic TOML configuration and 'Folded' interaction fabric.
- **Visualizer:** Interactive 3D/2D topological maps with live API data fetching.
- **Navigation:** 'Whistle' tool for seamless navigation between visualization modes (Topology, Apocalypse).

## Project Structure

- `src/core/loom/`: The mathematical and topological engine.
- `src/core/scanners/`: Modular code analysis engines.
- `src/visualizers/`: 3D and 2D data representation tools.
- `src/api/`: Integration layers.
- `tests/`: Unit and integration tests.
- `docs/`: Technical documentation.

## Roadmap

- [x] Phase 1: Project Scaffolding
- [ ] Phase 2: The 'Loom' Engine (Core)
- [ ] Phase 3: Modular Scanners
- [ ] Phase 4: Advanced Visualizers
- [ ] Phase 5: Workbench Integration & UI
