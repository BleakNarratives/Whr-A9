# EquiLex + GitHub Copilot Integration

## Purpose
This document helps Android developers use GitHub Copilot to accelerate `EquiLex` development and ship legal compliance tooling faster.

## Recommended workflow
1. Open `h:\IDE\EquiLex` in VS Code.
2. Install the recommended extensions from `.vscode/extensions.json`.
3. Use Copilot to complete or extend the CLI, the backend endpoints, and the VS Code extension commands.
4. Keep `equilex_cli.py` as the lightweight Termux entrypoint.

## Copilot prompts to use
### Generate a compliance template
```
Write a Python function that generates a GDPR-ready Android privacy policy template given a company name, product name, and jurisdiction.
Use the existing EquiLex CLI style and output a JSON object with `type`, `company_name`, `product_name`, `jurisdiction`, and `content`.
```

### Improve Android app review checks
```
Add Android Play Store compliance verification logic to the EquiLex CLI.
It should examine privacy policy text and detect if location permission, data collection, and third-party SDK disclosure are present.
```

### Build a VS Code command palette integration
```
Create a VS Code extension command called `EquiLex: Generate Privacy Policy`.
The command should prompt the user for company name, product name, and jurisdiction, then insert a generated policy into the active editor.
```

## Force multiplier commands
- `python equilex_cli.py analyze README.md`
- `python equilex_cli.py generate tos --company "MyApp" --product "MyApp" --jurisdiction "California"`
- `python equilex_cli.py snippet --package com.myapp --target android`

## Developer notes
- Keep the `tools/equilex-vscode-extension` folder as the extension prototype.
- Use Copilot to turn the prototype into a real `dist/extension.js` build step.
- For Termux, the CLI is the most powerful distribution path.
