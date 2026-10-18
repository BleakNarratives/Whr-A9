#!/usr/bin/env python3
"""
MOLT CLI v4: Retro 8-Bit Shenanigans Edition

This CLI provides an interactive, retro-themed interface for the Molt engine,
injecting playful personas into Ollama interactions.
"""

import sys
import time
import random
import os
import json # Import json for config loading
from pathlib import Path
from typing import List, Optional

# --- Dynamically adjust sys.path to import from the correct location ---
# Determine the base directory of the script (project root)
BASE_DIR = Path(__file__).parent
# The root molt.py engine should be importable directly as 'molt'
# The src modules should be importable as 'src.core', 'src.ui', etc.

# Add the base directory to sys.path to ensure 'molt' package is found
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
# Add src directory to sys.path if needed, though Python's import mechanism
# should handle 'from src.module' if __init__.py files are present.
if str(BASE_DIR / "src") not in sys.path:
     sys.path.insert(0, str(BASE_DIR / "src"))


try:
    # Import core Molt classes from the root molt.py engine
    from molt import Molt 
    # Explicitly import from src.core for modules within the src package
    from src.core.ollama_bridge import OllamaClient 
    from src.core.iterate import MoltIterator
    from src.ui.render import TreeRenderer
    from src.memory.improvements import ImprovementMemory
    # Assuming a config loader might be in src.config
    # Need to load config directly for pre-check
except ImportError as e:
    print(f"Error importing Molt modules: {e}")
    print("Please ensure the 'molt' package and 'src' directory structure are correctly set up")
    print("and that your Python environment has necessary dependencies installed.")
    print(f"Attempted to import from: {BASE_DIR} and {BASE_DIR / 'src'}")
    sys.exit(1)

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.prompt import Prompt
from rich.spinner import Spinner

console = Console()

# --- Retro 8-Bit Theme Colors and Styles ---
COLOR_PRIMARY = "dark_orange"  
COLOR_SECONDARY = "peru"       
COLOR_ACCENT_1 = "bold yellow" 
COLOR_ACCENT_2 = "bold bright_cyan" 
COLOR_WARN = "bold dark_orange"   
COLOR_ERROR = "bold magenta"    
COLOR_INFO = "light_blue"       
COLOR_BORDER = "gray42"        

# Retro ASCII Art Components
RETRO_BANNER = r"""
  .-.  .-.  .-.  .-.  .-.  .-.  .-.  .-.
 ( V ) ( 4 ) ( _ ) ( _ ) ( M ) ( O ) ( L ) ( T )
  `-'  `-'  `-'  `-'  `-'  `-'  `-'  `-'
   _/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/_/
  /                                       /|
 /  ____ ____ ____ ____ ____ ____ ____   / /
/  / __/ __/ __/ __/ __/ __/ __/ __/ __/ / /
\/ / / / / / / / / / / / / / / / / / / / /
 / / /_/ /_/ /_/ /_/ /_/ /_/ /_/ /_/ /_/
/_/

  8-BIT SHENANIGANS MODE ACTIVATED!
"""

# --- Layout Configuration ---
def create_layout() -> Layout:
    """Define the basic layout for the CLI with retro styling."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=12),
        Layout(name="main"),
        Layout(name="footer", size=3)
    )
    layout["main"].split_row(
        Layout(name="status_panel", ratio=1),
        Layout(name="info_panel", ratio=2)
    )
    return layout

def update_header(layout: Layout):
    """Update the header with the retro Molt banner and title."""
    header_text = Text(RETRO_BANNER, justify="center", style=COLOR_ACCENT_1)
    layout["header"].update(
        Panel(header_text, border_style=COLOR_BORDER, height=10)
    )

def generate_molt_status_table() -> Panel:
    """Generate a retro-themed Molt status display table."""
    table = Table(box=None, show_header=False, show_edge=False, padding=(0, 1))
    table.add_column(style=COLOR_PRIMARY)
    table.add_column(style=COLOR_SECONDARY)

    system_status = "[ONLINE]" if random.random() < 0.95 else "[OFFLINE?]"
    chaos_levels = ["LOW", "MEDIUM", "HIGH", "MAXIMAL", "UNHINGED"]
    fun_factors = ["LOW", "STANDARD", "HIGH", "EXTREME", "OFF THE CHARTS"]

    table.add_row(Text("SYSTEM STATUS", style=COLOR_ACCENT_2), Text(system_status, style=COLOR_PRIMARY if system_status == "[ONLINE]" else COLOR_ERROR))
    table.add_row("AGENT COUNT", f"{random.randint(4, 16)} active", style=COLOR_SECONDARY)
    table.add_row("CHAOS LEVEL", Text(random.choice(chaos_levels), style=COLOR_WARN if "MAXIMAL" in chaos_levels or "UNHINGED" in chaos_levels else COLOR_PRIMARY))
    table.add_row("FUN FACTOR", Text(random.choice(fun_factors), style=COLOR_ACCENT_1 if "EXTREME" in fun_factors or "OFF THE CHARTS" in fun_factors else COLOR_PRIMARY))
    table.add_row("INTEGRITY", Text(f"{random.uniform(85.5, 99.9):.1f}%", style=COLOR_PRIMARY))
    table.add_row("LATENCY", f"{random.randint(5, 60)}ms", style=COLOR_SECONDARY)
    table.add_row("MISSION STATUS", Text("GO!", style=COLOR_ACCENT_2))
    table.add_row("OMNI-SCAN", Text("ACTIVE", style=COLOR_PRIMARY))

    return Panel(
        Align.center(table, vertical="middle"),
        title=Text("RAMPANT SYSTEMS CORE", style=COLOR_ACCENT_1),
        border_style=COLOR_BORDER
    )

def generate_dynamic_info_panel(command_output: List[str], current_task: str = "", persona_applied: str = "") -> Panel:
    """Generate the dynamic info panel, showing output and mischievous messages."""
    output_lines = [line for line in command_output if line] 
    output_text = Text("\n".join(output_lines), style=COLOR_INFO)

    mischievous_messages = [
        "Processing... Engaging warp drive for silliness!",
        "Beep boop! Your request is being processed by giggling robots.",
        "Did you try turning it off and on again? Just kidding... mostly.",
        "Warning: May contain traces of pure awesome and questionable logic.",
        "System error: Too much fun detected. Adjusting parameters...",
        "Your input has been logged for... science!",
        "Is this the real life? Is this just fantasy? Anyway, here's your output.",
        "Engaging 'Mischief Mode'... Please stand by for unexpected results.",
        "Calculating optimal path to hilarity...",
    ]
    
    if current_task:
        mischievous_messages.append(f"Mastering '{current_task}' with retro flair!")
    if persona_applied:
        mischievous_messages.append(f"Persona Active: {persona_applied.strip()}")

    info_panel_content = Layout()
    info_panel_content.split_column(
        Panel(
            Align.left(output_text, vertical="top"),
            title=Text("OUTPUT LOG", style=COLOR_ACCENT_2),
            border_style=COLOR_BORDER,
            height=max(5, os.get_terminal_size().lines - 15) 
        ),
        Panel(
            Text(random.choice(mischievous_messages), justify="center", style=COLOR_WARN),
            title=Text("SYSTEM QUIRKS", style=COLOR_ACCENT_1),
            border_style=COLOR_BORDER
        )
    )
    return info_panel_content

def get_persona_options() -> List[str]:
    """Returns a list of available retro game persona instructions."""
    return [
        "Respond with a playful, retro game character's chaotic flair: ",
        "Inject silliness and unexpected twists, like an 8-bit NPC: ",
        "Adopt a slightly chaotic but helpful persona, like a glitchy game sprite: ",
        "Channel a mischievous sidekick from an old adventure game: ",
        "Respond as if you're a charmingly incompetent robot from a sci-fi B-movie: ",
        "Add a touch of retro-futuristic absurdity to your answer: ",
        "Respond with the wisdom of a wise-cracking ancient artifact: "
    ]

# Helper to load config for initial Ollama check
def _load_cli_config():
    config_path = BASE_DIR / 'src/config/config.json'
    if config_path.exists():
        try:
            with open(config_path) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def main():
    layout = create_layout()
    command_output = [Text("Welcome to MOLT v4! Type 'help' for commands.", style=COLOR_ACCENT_2)]
    current_task_description = ""
    current_persona_instruction = ""
    persona_applied_for_panel = "" # Store the actual chosen persona for display

    # --- Initial Ollama Connection Check ---
    cli_config = _load_cli_config()
    ollama_client_check = OllamaClient(
        host=cli_config.get('ollama_host', 'http://127.0.0.1:11434'),
        model=cli_config.get('model', 'deepseek-r1:1.5b')
    )
    is_connected, message = ollama_client_check.test_connection()
    if not is_connected:
        console.print(Panel(
            Text(f"❌ Ollama Initialization Error: {message}\n", style=COLOR_ERROR) +
            Text("Please ensure Ollama is running (`ollama serve`) and the configured model is available.", style=COLOR_INFO),
            title=Text("CRITICAL ERROR", style=COLOR_ERROR),
            border_style=COLOR_ERROR
        ))
        sys.exit(1)
    else:
        command_output.append(Text(f"✅ Ollama Status: {message}", style=COLOR_PRIMARY))
    # --- End Initial Ollama Connection Check ---


    with Live(layout, screen=True, refresh_per_second=4, transient=True) as live:
        # Initial render
        update_header(layout)
        layout["status_panel"].update(generate_molt_status_table())
        layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
        live.update(layout) # Initial update to show the layout

        while True:
            try:
                # Update status periodically for liveliness
                if random.random() < 0.6: 
                    layout["status_panel"].update(generate_molt_status_table())
                live.update(layout)

                # Prompt for user input with retro styling
                user_input = Prompt.ask(
                    Text(">>> ", style=COLOR_ACCENT_1),
                    spinner_style=COLOR_WARN
                )
                command_output.append(f">>> {user_input}")
                
                parts = user_input.strip().lower().split(maxsplit=1)
                cmd = parts[0] if parts else ""
                args = parts[1] if len(parts) > 1 else ""

                if cmd == "exit":
                    command_output.append(Text("Powering down retro systems. Stay pixelated!", style=COLOR_ACCENT_1))
                    layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
                    live.update(layout)
                    time.sleep(1)
                    break
                
                elif cmd == "help":
                    help_text = [
                        Text("--- COMMAND MENU ---", style=COLOR_ACCENT_2),
                        Text("iterate [your task]: Start Molt with retro persona. Example: 'iterate write a poem about pixel art'"),
                        Text("persona: Select or toggle persona instructions."),
                        Text("status: Show system status and mission details."),
                        Text("ping: Check system responsiveness."),
                        Text("clear: Wipe the output log."),
                        Text("help: Display this menu."),
                        Text("exit: Power down the CLI."),
                        Text("--- END MENU ---", style=COLOR_ACCENT_2)
                    ]
                    command_output.extend(help_text)

                elif cmd == "persona":
                    persona_options = get_persona_options()
                    # Add an option to disable personas
                    persona_options_with_disable = persona_options + ["Disable persona injection"]
                    
                    # Use Prompt.ask with choices for selection
                    selection_prompt_text = Text("Choose a persona (or disable it):", style=COLOR_ACCENT_1)
                    choices_for_prompt = [f"{i+1}. {opt}" for i, opt in enumerate(persona_options_with_disable)]
                    
                    selected_persona_str = Prompt.ask(
                        selection_prompt_text,
                        choices=choices_for_prompt,
                        show_choices=True,
                        default="1" # Default to first option
                    )
                    
                    # Parse selection
                    try:
                        # Extract number and handle potential '. ' after number
                        choice_num_str = selected_persona_str.split('.')[0].split(' ')[0]
                        choice_num = int(choice_num_str)
                        
                        if choice_num > len(persona_options): # User selected "Disable persona"
                            current_persona_instruction = ""
                            persona_applied_for_panel = "Disabled"
                            command_output.append(Text("Persona injection disabled. Retro fun reduced, but systems stable.", style=COLOR_INFO))
                        else:
                            current_persona_instruction = persona_options[choice_num - 1]
                            persona_applied_for_panel = current_persona_instruction.strip()
                            command_output.append(Text(f"Persona set: '{persona_applied_for_panel}'", style=COLOR_INFO))
                    except (ValueError, IndexError):
                        command_output.append(Text("Invalid persona selection. Please choose a number.", style=COLOR_ERROR))
                        current_persona_instruction = "" # Reset on error
                        persona_applied_for_panel = "Error"

                elif cmd == "iterate":
                    if not args:
                        command_output.append(Text("Mission objective required! Use 'iterate [your task here]'.", style=COLOR_ERROR))
                    else:
                        current_task_description = args
                        task_with_persona = current_persona_instruction + args # Use selected persona
                        
                        command_output.append(Text(f"🚀 Initiating chaotic iteration on: '{args}'", style=COLOR_ACCENT_2))
                        if current_persona_instruction:
                            command_output.append(Text(f"   Persona Directive: '{current_persona_instruction.strip()}'", style=COLOR_SECONDARY))

                        spinner = Spinner("dots", text=Text("Processing... engaging retro-logic!", style=COLOR_ACCENT_1))
                        layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
                        layout["info_panel"].loading = spinner # Indicate loading state
                        live.update(layout)

                        # Execute Molt iteration
                        molt = Molt() # Initialize Molt, which uses OllamaClient
                        
                        # Use default iterations from config or Molt class if available
                        molt_max_iterations = molt.config.get('default_iterations', 5) 
                        
                        result = molt.run(task_with_persona, max_iterations=molt_max_iterations)
                        
                        # Check for error in result from Molt.run
                        if 'error' in result:
                            command_output.append(Text(f"❌ Iteration failed: {result['error']}", style=COLOR_ERROR))
                        else:
                            # Update output after completion
                            score = result.get('score', 0)
                            command_output.append(f"✅ Iteration complete! Final Score: {score:.2f}")
                            best_output_snippet = result.get('output', 'N/A')[:200] + ('...' if len(result.get('output', '')) > 200 else '')
                            command_output.append(f"   Best Output Snippet: {best_output_snippet}")
                        current_task_description = "" # Clear task description after completion

                elif cmd == "status":
                    status_panel = generate_molt_status_table()
                    rendered_status = status_panel.renderable.render(console, console.options).text.strip()
                    command_output.append(Text("--- SYSTEM STATUS ---", style=COLOR_ACCENT_2))
                    command_output.append(Text(rendered_status, style=COLOR_PRIMARY))
                    command_output.append(Text("--- END STATUS ---", style=COLOR_ACCENT_2))

                elif cmd == "ping":
                    latency = random.randint(5, 60)
                    command_output.append(f"Pinging MoltNet... Latency detected: {latency}ms. All systems nominal... for now.")
                
                elif cmd == "clear":
                    command_output = [Text("Output log cleared. Ready for new shenanigans!", style=COLOR_INFO)]
                
                elif cmd: # Handle any other non-empty command that wasn't matched
                    command_output.append(Text(f"Command '{user_input}' not recognized. Type 'help' for options.", style=COLOR_ERROR))
                
                # Keep output buffer from growing indefinitely
                max_output_lines = max(5, os.get_terminal_size().lines - 15) 
                if len(command_output) > max_output_lines:
                    command_output = command_output[-max_output_lines:]

                # Update info panel and refresh live display
                layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
                layout["info_panel"].loading = None # Remove spinner if it was active
                live.update(layout)
                time.sleep(0.05) # Small delay for smooth rendering and responsiveness

            except KeyboardInterrupt:
                command_output.append(Text("Aborting mission! Powering down...", style=COLOR_ERROR))
                layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
                live.update(layout)
                time.sleep(0.5)
                break
            except Exception as e:
                error_msg = Text(f"CRITICAL ERROR: {type(e).__name__} - {e}", style=COLOR_ERROR)
                command_output.append(error_msg)
                layout["info_panel"].update(generate_dynamic_info_panel(command_output, current_task_description, persona_applied_for_panel))
                live.update(layout)
                time.sleep(0.5)

    console.print(Text("\n     Session Ended. Stay mischievous!\n", style=COLOR_ACCENT_2, justify="center"))

if __name__ == "__main__":
    main()
