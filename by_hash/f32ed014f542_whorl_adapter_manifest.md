# Whorl Adapter Manifest

## Purpose

Reserve a clean interface for the agentic helical coding language runtime.
This cockpit should not assume Whorl internals. It should discover capabilities
through an adapter.

## Expected Adapter Shape

- `whorl doctor`: report runtime status.
- `whorl modules`: list installed language modules.
- `whorl trace <target>`: emit an execution trace for cockpit playback.
- `whorl run <target>`: execute a trusted target.

## UI Surfaces

- Runtime status card.
- Trace timeline.
- Agent handoff panel.
- Source-to-spiral visualization.

Generated locally at 2026-05-13 16:16:50.
