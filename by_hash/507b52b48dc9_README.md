# MoltBleak - Retro 8-Bit Shenanigans CLI

Welcome to MoltBleak, a project featuring a retro 8-bit themed CLI (`molt_cli_v4.py`) for interacting with the Molt engine. Molt is a recursive self-improvement system that iteratively refines tasks, now enhanced with playful persona injection for Ollama interactions.

## Core Features

*   **Retro 8-Bit CLI (`molt_cli_v4.py`):** An interactive command-line interface with a nostalgic 70s/80s aesthetic, complete with playful messages and retro styling. Includes:
    *   **Initial Ollama Connection Check:** Verifies Ollama connectivity and model availability at startup.
    *   **Mischievous Persona Injection:** When using the `iterate` command, the CLI can prepend a retro game character persona to your task, influencing Ollama's responses with chaotic flair. You can select or disable personas.
    *   **Robust Error Handling:** Provides clear feedback on Molt and Ollama-related errors.
*   **Recursive Self-Improvement (Molt Engine):** The core `molt.py` engine refines tasks through multiple iterations, aiming for better outputs. It now includes enhanced error handling from Ollama.
*   **Ollama Integration:** Runs locally using your Ollama instance for AI model interactions, with improved, granular error reporting.
*   **Organized Project Structure:** Clean layout for easy access to executables and core logic.

## Project Structure

```
MoltBleak/
├── README.md                   # Project overview and instructions
├── LICENSE                     # (If applicable)
├── molt_cli_v4.py              # <<< Your retro-themed interactive CLI
├── molt.py                     # Core Molt engine (consolidated source)
├── requirements.txt            # Project dependencies
├── test_connection.py          # Utility script for Ollama connection testing
├── bin/                        # Scripts that are directly executable or utilities
│   ├── bin_scripts/            # Installer and setup scripts
│   │   ├── install_molt.sh
│   │   ├── molt_install.sh
│   │   ├── operation_schmoperation.sh
│   │   └── setup_cli.sh
│   └── telegramining/          # Grouping 'the_telegramining' scripts
│       ├── mikey_mind_palace_excavator.py
│       ├── mikey_mind_palace_metadata.py
│       ├── mikey_palace_full.py
│       ├── reaper_v3.py
│       ├── tele_cram.py
│       └── ... (any other telegramining files)
└── src/                        # Core Molt logic, separated from executables
    ├── __init__.py
    ├── core/                   # Molt's core modules (iterate, ollama_bridge)
    │   ├── __init__.py
    │   ├── iterate.py
    │   ├── ollama_bridge.py
    │   └── ...
    ├── ui/                     # Molt's UI rendering logic (TreeRenderer)
    │   ├── __init__.py
    │   ├── render.py
    │   └── ...
    ├── memory/                 # Molt's memory management
    │   ├── __init__.py
    │   ├── improvements.py
    │   └── ...
    ├── prompts/                # Molt prompt templates
    │   ├── __init__.py
    │   ├── system.txt
    │   └── templates/
    │       └── ...
    └── config/                 # Configuration files
        ├── __init__.py
        ├── config.json
        ├── molt_config_optimized.json
        └── ...
├── archive/                    # Archived older versions and scripts (will be zipped)
│   ├── old_clis/
│   │   ├── molt_cli_v3.py
│   │   ├── molt_cli.py
│   │   └── molt_cli_v2.py
│   ├── bin_scripts/
│   │   └── ... (installer scripts from original molt/ directory)
│   └── telegramining_scripts/
│       └── ... (telegramining scripts originally from 'the_telegramining/')
```

## Getting Started

### Prerequisites
*   **Ollama:** Ensure Ollama is installed and running locally. You can download it from [https://ollama.com/](https://ollama.com/).
*   **Python:** Python 3.8+ recommended.
*   **Ollama Models:** Install at least one model compatible with Molt (e.g., `deepseek-r1:1.5b` or `qwen2.5:0.5b`). Use `ollama pull <model_name>`.

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd MoltBleak
    ```
    *(If you are not using git, ensure files are placed according to the structure above)*

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(The `requirements.txt` should include `rich`, `requests`, etc.)*

3.  **Configure Ollama:**
    Check or edit `src/config/config.json` if your Ollama host or model name differs from the defaults (`http://127.0.0.1:11434` and `deepseek-r1:1.5b`).

4.  **Test Ollama Connection:**
    ```bash
    python test_connection.py
    ```
    This script will verify if Molt can connect to your Ollama instance and use the configured model, providing detailed feedback.

### Usage

#### Using `molt_cli_v4.py` (Retro Shenanigans CLI)

This is the primary interactive CLI for Molt.

1.  **Start the CLI:**
    ```bash
    python molt_cli_v4.py
    ```
2.  **Interact with Commands:**
    *   **`help`**: Displays available commands.
    *   **`iterate [your task]`**: Starts a Molt session. Your task will be enhanced with a retro game persona instruction for Ollama.
        *   Example: `iterate write a poem about pixel art`
        *   Example: `iterate explain the concept of recursion in a funny way`
    *   **`persona`**: Allows you to select a different persona for Molt's responses or disable persona injection.
    *   **`status`**: Shows system information and mission details.
    *   **`ping`**: Checks system responsiveness.
    *   **`clear`**: Wipes the output log.
    *   **`exit`**: Powers down the CLI.

#### Using `molt.py` (Core Engine)

You can also run the core Molt engine directly from the command line for basic task iteration.

```bash
python molt.py "your task here"
```

This will run Molt with default settings, visualizing the growth process in a text-based tree format. Any errors during Ollama interaction will be reported.

## Future Enhancements & Autonomous Agent Perspective

As Project Lead, I've considered your request for "automation inside the interface for hands-free builds and project completion" and the ability to "figure out what it needs and kind of guess my intent." This is a vision for a highly advanced AI development assistant. While the current Molt engine excels at recursive self-improvement of *given tasks*, achieving full "hands-free project completion" through folder analysis and intent inference would require significant architectural expansion.

Future considerations to move towards this vision could include:

*   **Project Contextualization:** Developing modules to analyze project files, infer technologies, and identify common development tasks.
*   **Task Decomposition:** An AI orchestrator to break down high-level project goals into smaller, iterative Molt tasks.
*   **Feedback Loop Integration:** Mechanisms for Molt to receive feedback from build systems, linters, and tests, allowing for autonomous self-correction and continuous improvement in a broader development context.
*   **Domain-Specific Molt:** Training specialized Molt instances for different programming languages or project types.

This is a journey into the frontier of autonomous software engineering, and a fascinating one.

---
*Built with 8-bit chaos for modern minds.*
```