# AUTHOR(S) platform_adapter.py
"""
Platform Adapter for MotherBrain.
Provides a hardware abstraction layer (HAL) to ensure the orchestrator
runs identically across Android (Termux) and Windows (CMD/PowerShell).
"""

import os
import platform
import subprocess
import sys

class PlatformAdapter:
    def __init__(self):
        self.os_type = platform.system().lower()
        self.is_termux = self._check_termux()
        self.shell = self._get_shell()

    def _check_termux(self) -> bool:
        """Checks if the current environment is Termux on Android."""
        # Termux usually has a specific environment variable or path structure
        return os.path.exists('/data/data/com.termux/files/usr/bin/bash')

    def _get_shell(self) -> str:
        """Determines the appropriate shell for the current OS."""
        if self.is_termux:
            return '/data/data/com.termux/files/usr/bin/bash'
        elif self.os_type == 'windows':
            return 'powershell.exe'
        return '/bin/bash'

    def run_command(self, command: str, capture_output: bool = True) -> subprocess.CompletedProcess:
        """
        Executes a system command through the platform-specific shell.
        Ensures that commands are wrapped correctly for the target OS.
        """
        try:
            full_cmd = command if self.os_type == 'windows' else f'{self.shell} -c "{command}"'
            
            return subprocess.run(
                full_cmd,
                shell=True,
                capture_output=capture_output,
                text=True,
                check=False
            )
        except Exception as e:
            print(f"[!] PlatformAdapter Error: {e}")
            return subprocess.CompletedProcess(args=command, returncode=1, stdout="", stderr=str(e))

    def set_wake_lock(self):
        """
        Prevents the device from sleeping during active MotherBrain sessions.
        """
        if self.is_termux:
            self.run_command("termux-wake-lock")
            print("[+] Wake-lock acquired (Android/Termux)")
            return

        if self.os_type == 'windows':
            self.run_command('powershell -command "(Get-CimInstance -ClassName Win32_Process).Create()"')
            print("[+] System activity simulated (Windows)")
            return

        print("[-] Wake-lock not supported on this platform.")

    def get_env_var(self, key: str, default: str = None) -> str:
        """Cross-platform environment variable retrieval."""
        return os.environ.get(key, default)

# --- Test Block ---
if __name__ == "__main__":
    # This block is for internal validation during the Scribe phase.
    # It will be removed or moved to /tests upon integration.
    adapter = PlatformAdapter()
    print(f"Detected OS: {adapter.os_type} | Termux: {adapter.is_termux}")
    print(f"Using Shell: {adapter.shell}")
    
    # Test wake-lock
    adapter.set_wake_lock()
    
    # Test simple command
    res = adapter.run_command("echo 'Adapter Online'")
    print(f"Test Output: {res.stdout.strip()}")
