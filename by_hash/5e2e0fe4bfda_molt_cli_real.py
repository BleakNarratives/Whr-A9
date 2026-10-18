#!/usr/bin/env python3
"""
MOLT CLI - Retro Terminal Interface with Real Functionality
"""
import time
import random
import os
import sys
from typing import List
from pathlib import Path

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.prompt import Prompt

# Import actual molt functionality
sys.path.insert(0, str(Path.home() / 'Code-City-Claude/MoltBleak/openclaw/molt'))
try:
    from core.multi_backend import MultiBackend
    from core.iterate import MoltIterator
    from memory.improvements import ImprovementMemory
    import json
    MOLT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import molt modules: {e}")
    MOLT_AVAILABLE = False

console = Console()

# --- ASCII Art & Styling ---
MOLT_BANNER = r"""
███╗   ███╗ ██████╗ ██╗     ████████╗
████╗ ████║██╔═══██╗██║     ╚══██╔══╝
██╔████╔██║██║   ██║██║        ██║   
██║╚██╔╝██║██║   ██║██║        ██║   
██║ ╚═╝ ██║╚██████╔╝███████╗   ██║   
╚═╝     ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
"""

# Color palette
COLOR_ACCENT_1 = "bold bright_red"
COLOR_ACCENT_2 = "bold bright_green"
COLOR_PRIMARY = "green"
COLOR_SECONDARY = "dim yellow"
COLOR_ERROR = "bold red"
COLOR_WARN = "bold yellow"
COLOR_INFO = "cyan"
COLOR_BORDER = "bright_black"

class MoltCLI:
    def __init__(self):
        self.command_output = ["Welcome to Molt CLI. Type 'help' for commands.", ""]
        self.molt_config = self.load_config()
        
        if MOLT_AVAILABLE:
            self.backend = MultiBackend(self.molt_config)
            self.iterator = MoltIterator(self.backend)
            self.memory = ImprovementMemory(Path.home() / 'Code-City-Claude/MoltBleak/openclaw/molt/memory')
            self.backend_health = {}
            self.update_backend_health()
        else:
            self.backend = None
            self.iterator = None
            self.memory = None
            self.backend_health = {}
    
    def load_config(self):
        """Load molt configuration"""
        config_path = Path.home() / 'Code-City-Claude/MoltBleak/openclaw/molt/config.json'
        try:
            if config_path.exists():
                with open(config_path) as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"Config load error: {e}", COLOR_WARN)
        
        return {
            "ollama_host": "http://127.0.0.1:11434",
            "ollama_model": "deepseek-r1:1.5b",
            "use_multi_backend": True
        }
    
    def update_backend_health(self):
        """Check health of all backends"""
        if self.backend:
            try:
                self.backend_health = self.backend.health_check()
            except Exception as e:
                self.log(f"Health check failed: {e}", COLOR_ERROR)
                self.backend_health = {}
    
    def log(self, message: str, style: str = COLOR_INFO):
        """Add message to command output"""
        self.command_output.append(Text(message, style=style))
        
        # Keep buffer manageable
        if len(self.command_output) > 50:
            self.command_output = self.command_output[-50:]
    
    def create_layout(self) -> Layout:
        """Define the basic layout for the CLI."""
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", size=10),
            Layout(name="main"),
            Layout(name="footer", size=3)
        )
        layout["main"].split_row(
            Layout(name="status_panel", ratio=1),
            Layout(name="info_panel", ratio=2)
        )
        return layout

    def update_header(self, layout: Layout):
        """Update the header with the Molt banner."""
        header_text = Text(MOLT_BANNER, justify="left", style=COLOR_ACCENT_1)
        layout["header"].update(
            Panel(header_text, border_style=COLOR_BORDER, title_align="left")
        )

    def generate_status_table(self) -> Panel:
        """Generate real-time Molt status display."""
        table = Table(box=None, show_header=False, show_edge=False, padding=(0, 1))
        table.add_column(style=COLOR_PRIMARY)
        table.add_column(style=COLOR_SECONDARY)

        # Real status
        molt_status = "ONLINE" if MOLT_AVAILABLE else "OFFLINE"
        status_color = COLOR_PRIMARY if MOLT_AVAILABLE else COLOR_ERROR
        
        table.add_row(Text("SYSTEM STATUS", style=COLOR_ACCENT_2), Text(f"[{molt_status}]", style=status_color))
        
        # Backend health
        if self.backend_health:
            working_backends = sum(1 for v in self.backend_health.values() if v)
            total_backends = len(self.backend_health)
            table.add_row("BACKENDS", f"{working_backends}/{total_backends} active", style=COLOR_SECONDARY)
            
            for backend, healthy in self.backend_health.items():
                status = "✓" if healthy else "✗"
                color = COLOR_PRIMARY if healthy else COLOR_ERROR
                table.add_row(f"  {backend}", Text(status, style=color))
        
        # Memory stats
        if self.memory:
            tasks = self.memory.list_tasks()
            table.add_row("MEMORY", f"{len(tasks)} tasks stored", style=COLOR_SECONDARY)
        
        table.add_row("LATENCY", f"{random.randint(10, 50)}ms", style=COLOR_SECONDARY)

        return Panel(
            Align.center(table, vertical="middle"),
            title=Text("MOLT SYSINFO", style=COLOR_ACCENT_1),
            border_style=COLOR_BORDER
        )

    def generate_info_panel(self) -> Panel:
        """Generate the dynamic info panel."""
        output_text = Text("\n".join([str(line) for line in self.command_output[-20:]]), style=COLOR_INFO)

        devious_messages = [
            "Thinking thoughts you haven't considered...",
            "Processing... or are you?",
            "Watching the watchers watch you.",
            "System stable. For now.",
            "Error 404: Ethics not found.",
            "What secrets will we unravel next?",
            "Don't worry. Your data is perfectly safe. Probably."
        ]

        info_content = Layout()
        try:
            terminal_height = os.get_terminal_size().lines
        except:
            terminal_height = 24
        
        info_content.split_column(
            Panel(output_text, title=Text("OUTPUT", style=COLOR_ACCENT_2), border_style=COLOR_BORDER),
            Panel(Text(random.choice(devious_messages), justify="center", style=COLOR_WARN), 
                  border_style=COLOR_BORDER, height=3)
        )
        return info_content
    
    def cmd_help(self, args: str):
        """Show available commands"""
        commands = {
            "help": "Show this help",
            "status": "Display system status",
            "health": "Check backend health",
            "iterate <task>": "Run molt iteration on task",
            "memory": "List stored improvements",
            "best <task>": "Get best result for task",
            "config": "Show current configuration",
            "clear": "Clear output",
            "exit": "Exit Molt CLI"
        }
        
        self.log("═══ AVAILABLE COMMANDS ═══", COLOR_ACCENT_2)
        for cmd, desc in commands.items():
            self.log(f"  {cmd:<20} {desc}", COLOR_PRIMARY)
    
    def cmd_status(self, args: str):
        """Display detailed status"""
        self.log("═══ SYSTEM STATUS ═══", COLOR_ACCENT_2)
        self.log(f"Molt Available: {MOLT_AVAILABLE}", COLOR_PRIMARY if MOLT_AVAILABLE else COLOR_ERROR)
        
        if self.backend_health:
            self.log("Backend Status:", COLOR_PRIMARY)
            for backend, healthy in self.backend_health.items():
                status = "ONLINE" if healthy else "OFFLINE"
                color = COLOR_PRIMARY if healthy else COLOR_ERROR
                self.log(f"  {backend}: {status}", color)
    
    def cmd_health(self, args: str):
        """Check backend health"""
        self.log("Checking backend health...", COLOR_INFO)
        self.update_backend_health()
        
        if self.backend_health:
            for backend, healthy in self.backend_health.items():
                status = "✓ HEALTHY" if healthy else "✗ OFFLINE"
                color = COLOR_PRIMARY if healthy else COLOR_ERROR
                self.log(f"{backend}: {status}", color)
        else:
            self.log("No backends available", COLOR_WARN)
    
    def cmd_iterate(self, task: str):
        """Run molt iteration"""
        if not MOLT_AVAILABLE:
            self.log("Molt not available. Check installation.", COLOR_ERROR)
            return
        
        if not task:
            self.log("Usage: iterate <task>", COLOR_WARN)
            return
        
        self.log(f"🌱 Starting iteration on: {task}", COLOR_ACCENT_2)
        
        try:
            results = []
            for i in range(3):  # 3 iterations
                self.log(f"  Ring {i+1}...", COLOR_INFO)
                result = self.iterator.iterate(task, results)
                results.append(result)
                
                score = result.get('score', 0)
                is_improvement = result.get('is_improvement', False)
                
                if is_improvement:
                    self.log(f"  ✓ Improvement! Score: {score:.2f}", COLOR_PRIMARY)
                    self.memory.store(task, result)
                else:
                    self.log(f"  - Score: {score:.2f}", COLOR_SECONDARY)
            
            # Get best result
            best = self.memory.get_best(task)
            if best:
                self.log(f"🌳 Best result (score {best['score']:.2f}):", COLOR_ACCENT_2)
                self.log(best['output'][:200] + "...", COLOR_PRIMARY)
        
        except Exception as e:
            self.log(f"Iteration failed: {e}", COLOR_ERROR)
    
    def cmd_memory(self, args: str):
        """List stored improvements"""
        if not self.memory:
            self.log("Memory not available", COLOR_ERROR)
            return
        
        tasks = self.memory.list_tasks()
        
        if not tasks:
            self.log("No tasks in memory", COLOR_WARN)
            return
        
        self.log(f"═══ STORED TASKS ({len(tasks)}) ═══", COLOR_ACCENT_2)
        for task in tasks[:10]:  # Show first 10
            self.log(f"  • {task[:60]}...", COLOR_PRIMARY)
    
    def cmd_best(self, task: str):
        """Get best result for task"""
        if not self.memory:
            self.log("Memory not available", COLOR_ERROR)
            return
        
        if not task:
            self.log("Usage: best <task>", COLOR_WARN)
            return
        
        best = self.memory.get_best(task)
        
        if not best:
            self.log(f"No results found for: {task}", COLOR_WARN)
            return
        
        self.log(f"Best result (score {best['score']:.2f}):", COLOR_ACCENT_2)
        self.log(best['output'], COLOR_PRIMARY)
    
    def cmd_config(self, args: str):
        """Show configuration"""
        self.log("═══ CONFIGURATION ═══", COLOR_ACCENT_2)
        for key, value in self.molt_config.items():
            self.log(f"  {key}: {value}", COLOR_PRIMARY)
    
    def process_command(self, user_input: str):
        """Process user command"""
        self.command_output.append(f">>> {user_input}")
        
        parts = user_input.split(maxsplit=1)
        cmd = parts[0].lower() if parts else ""
        args = parts[1] if len(parts) > 1 else ""
        
        commands = {
            'help': self.cmd_help,
            'status': self.cmd_status,
            'health': self.cmd_health,
            'iterate': self.cmd_iterate,
            'memory': self.cmd_memory,
            'best': self.cmd_best,
            'config': self.cmd_config,
        }
        
        if cmd == 'exit':
            return False
        elif cmd == 'clear':
            self.command_output = [""]
        elif cmd in commands:
            commands[cmd](args)
        elif cmd:
            self.log(f"Unknown command: '{cmd}'. Type 'help' for commands.", COLOR_ERROR)
        
        return True

    def run(self):
        """Main CLI loop"""
        layout = self.create_layout()
        
        with Live(layout, screen=True, refresh_per_second=4, transient=True) as live:
            self.update_header(layout)
            layout["status_panel"].update(self.generate_status_table())
            layout["info_panel"].update(self.generate_info_panel())
            
            while True:
                try:
                    # Periodic status update
                    if random.random() < 0.3:
                        layout["status_panel"].update(self.generate_status_table())
                    
                    live.refresh()
                    
                    user_input = Prompt.ask(Text(">>> ", style=COLOR_ACCENT_1))
                    
                    if not self.process_command(user_input):
                        self.log("Molt CLI powering down...", COLOR_ACCENT_1)
                        layout["info_panel"].update(self.generate_info_panel())
                        live.refresh()
                        time.sleep(1)
                        break
                    
                    layout["info_panel"].update(self.generate_info_panel())
                    time.sleep(0.1)
                
                except KeyboardInterrupt:
                    self.log("Interrupted. Exiting Molt CLI.", COLOR_ACCENT_1)
                    layout["info_panel"].update(self.generate_info_panel())
                    live.refresh()
                    time.sleep(0.5)
                    break
                except Exception as e:
                    self.log(f"CLI Error: {e}", COLOR_ERROR)
                    layout["info_panel"].update(self.generate_info_panel())
                    live.refresh()
        
        console.print(Text("\nSession ended. Stay devious.", style=COLOR_ACCENT_2, justify="center"))

def main():
    cli = MoltCLI()
    cli.run()

if __name__ == "__main__":
    main()
