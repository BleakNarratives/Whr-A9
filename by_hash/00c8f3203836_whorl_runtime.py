# AUTHOR(S) whorl_runtime.py
"""
Whorl Runtime: The Structural Orchestrator.
Executes compiled Whorl patterns by coordinating between 
the WhorlScribe and the PlatformAdapter.
"""

import os
import json
from typing import Dict, Any
from platform_adapter import PlatformAdapter
from whorl_scribe import WhorlScribe

class WhorlRuntime:
    def __init__(self):
        self.adapter = PlatformAdapter()
        self.scribe = WhorlScribe(self.adapter)

    def execute_pattern(self, pattern: Dict[str, Any]):
        """
        Executes a Whorl pattern from start to finish.
        """
        print(f"[*] Initiating Whorl Pattern: {pattern.get('name', 'Unnamed')}")
        
        compiled_cmds = self.scribe.compile_pattern(pattern)
        
        for description, cmd in compiled_cmds:
            print(f"  -> {description}")
            
            if cmd.startswith("__WHORL_SCAN__:"):
                self._handle_scan(cmd)
            elif cmd.startswith("__WHORL_RECURSE__:"):
                self._handle_recurse(cmd)
            else:
                # Standard command execution
                result = self.adapter.run_command(cmd)
                if result.returncode != 0:
                    print(f"    [!] Execution failed: {result.stderr}")

    def _handle_scan(self, encoded_cmd: str):
        """
        Handles the specialized scan logic: Find files -> Apply Action.
        """
        # Format: __WHORL_SCAN__:action:command
        parts = encoded_cmd.split(":", 2)
        if len(parts) < 3:
            return

        action, find_cmd = parts[1], parts[2]
        result = self.adapter.run_command(find_cmd)
        
        if result.returncode != 0 or not result.stdout:
            print("    [-] No files matched the scan pattern.")
            return

        files = result.stdout.strip().split("\n")
        for file in files:
            if not file: 
                continue
            self._apply_scan_action(file, action)

    def _apply_scan_action(self, file: str, action: str):
        """Helper to execute the specific action on a scanned file."""
        if action == "archive":
            self.adapter.run_command("mkdir -p archive")
            cmd = f'mv "{file}" archive/' if self.adapter.os_type != 'windows' else f'Move-Item -Path "{file}" -Destination archive/'
            print(f"    [+] Archived: {file}")
        elif action == "delete":
            cmd = f'rm "{file}"' if self.adapter.os_type != 'windows' else f'Remove-Item -Path "{file}"'
            print(f"    [+] Deleted: {file}")
        else:
            return

        self.adapter.run_command(cmd)

    def _handle_recurse(self, encoded_cmd: str):
        """
        Handles recursive directory processing.
        """
        # Format: __WHORL_RECURSE__:directive:path
        parts = encoded_cmd.split(":", 2)
        if len(parts) < 3:
            return

        directive_name, base_path = parts[1], parts[2]
        
        try:
            list_cmd = self._get_list_dir_cmd(base_path)
            result = self.adapter.run_command(list_cmd)
            
            if result.returncode != 0 or not result.stdout:
                return

            subdirs = result.stdout.strip().split("\n")
            for subdir in subdirs:
                if not subdir or subdir == base_path:
                    continue
                self._execute_sub_directive(subdir, directive_name)
        except Exception as e:
            print(f"    [!] Recursion Error in {base_path}: {e}")

    def _get_list_dir_cmd(self, path: str) -> str:
        """Helper to get platform-specific directory listing command."""
        if self.adapter.os_type == 'windows':
            return f"Get-ChildItem -Path '{path}' -Directory | Select-Object -ExpandProperty FullName"
        return f"find {path} -maxdepth 1 -type d"

    def _execute_sub_directive(self, path: str, directive: str):
        """Helper to execute a recursive sub-pattern."""
        sub_pattern = {
            "name": f"Sub-Task: {directive}",
            "directives": [{"type": directive, "path": path}]
        }
        self.execute_pattern(sub_pattern)

if __name__ == "__main__":
    # Internal validation test
    runtime = WhorlRuntime()
    
    # Define a sample pattern for testing
    # This pattern looks for files containing "test_whorl" and archives them
    test_pattern = {
        "name": "Whorl System Test",
        "directives": [
            {
                "type": "scan",
                "path": ".",
                "pattern": "test_whorl.*\.txt",
                "action": "archive"
            }
        ]
    }
    
    # Create a dummy file to test
    with open("test_whorl_1.txt", "w") as f: f.write("test data")
    
    runtime.execute_pattern(test_pattern)
