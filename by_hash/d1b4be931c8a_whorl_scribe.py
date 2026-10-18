# AUTHOR(S) whorl_scribe.py
"""
Whorl Scribe: The Structural Compiler.
Translates high-level Whorl Patterns (Intent) into concrete 
platform-specific shell commands (Execution).
"""

import re
import os
from typing import List, Dict, Any, Tuple

class WhorlScribe:
    def __init__(self, adapter):
        """
        Initialize the Scribe with a PlatformAdapter to ensure
        command generation is target-aware.
        """
        self.adapter = adapter

    def compile_pattern(self, pattern_dict: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Compiles a Whorl Pattern into a sequence of (description, command) tuples.
        """
        commands = []
        for directive in pattern_dict.get("directives", []):
            d_type = directive.get("type")
            
            if d_type == "scan":
                commands.extend(self._compile_scan(directive))
            elif d_type == "recurse":
                commands.extend(self._compile_recurse(directive))
            elif d_type == "verify_manifest":
                commands.extend(self._compile_manifest_check(directive))
            else:
                commands.append(("ERROR", f"Unknown directive type: {d_type}"))
                
        return commands

    def _compile_scan(self, directive: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Translates a 'scan' intent into a set of move/delete commands.
        """
        path = directive.get("path", ".")
        regex_pattern = directive.get("pattern", "")
        action = directive.get("action", "archive")
        
        find_cmd = self._get_find_command(path, regex_pattern)
        
        # Tag the command so the runtime knows it needs post-processing.
        return [(f"Scanning {path} for {regex_pattern}", f"__WHORL_SCAN__:{action}:{find_cmd}")]

    def _get_find_command(self, path: str, pattern: str) -> str:
        """Helper to generate platform-specific find commands."""
        if self.adapter.os_type == 'windows':
            return f"Get-ChildItem -Path '{path}' -Filter '*':* | Where-Object {{ $_.Name -match '{pattern}' }} | Select-Object -ExpandProperty FullName"
        return f"find {path} -maxdepth 1 -regex '.*{pattern}.*'"

    def _compile_recurse(self, directive: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Translates a 'recurse' intent.
        """
        path = directive.get("path", ".")
        sub_directive = directive.get("directive")
        
        # Recursion is handled by the runtime, the scribe just provides 
        # the target paths.
        commands = [(f"Recursing into {path} for {sub_directive}", f"__WHORL_RECURSE__:{sub_directive}:{path}")]
        return commands

    def _compile_manifest_check(self, directive: Dict[str, Any]) -> List[Tuple[str, str]]:
        """
        Translates a 'verify_manifest' intent.
        """
        path = directive.get("path", ".")
        # Check for existence of README.md or manifest.json
        if self.adapter.os_type == 'windows':
            check_cmd = f"Test-Path '{path}/README.md' -or (Test-Path '{path}/manifest.json')"
        else:
            check_cmd = f"[ -f {path}/README.md ] || [ -f {path}/manifest.json ]"
            
        return [(f"Verifying manifest in {path}", check_cmd)]
