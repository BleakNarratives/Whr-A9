# EquiLex Force Multiplier

## Mission
Make EquiLex the go-to Android developer legal compliance and wrapper toolkit, optimized for Termux, GitHub Copilot, and developer velocity.

## What was delivered
- `equilex_cli.py`: a Termux-friendly CLI for legal analysis, Android app compliance checks, template generation, and wrapper snippets.
- `.vscode/extensions.json`: recommends Copilot, Python, and GitLens so the workspace is ready for smart coding.
- `backend/api/routes.py` and backend service stubs are now ready for real FastAPI endpoints.
- A lightweight VS Code extension scaffold under `tools/equilex-vscode-extension`.
- Copilot integration guidance and product planning notes.

## Force Multiplier Strategy
1. Ship the CLI as the primary developer interface.
2. Add Copilot prompts and workspace recommendations.
3. Build a small VS Code extension that surfaces EquiLex commands in the editor.
4. Use the CLI output as the source of truth for generated policies, reports, and wrapper snippets.

## Quick wins
- Run `python equilex_cli.py analyze path/to/privacy.txt` from Termux or Windows.
- Run `python equilex_cli.py generate privacy_policy --company "Acme Apps" --product "AppGuard"`
- Open the `EquiLex` workspace in VS Code and install the recommended extensions.

## Next-level multiplier
- Add `equilex_cli.py` to a GitHub Actions workflow for automatic legal template generation.
- Create a Copilot prompt file that tells Copilot how to extend EquiLex for Android-specific developer workflows.
- Extend the VS Code extension to trigger CLI commands from the command palette.
