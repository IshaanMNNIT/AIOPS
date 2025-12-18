import subprocess
from typing import List, Dict


class CommandExecutor:
    ALLOWED_COMMANDS = {"ls", "pwd", "echo"}

    def run(self, command: List[str]) -> Dict:
        if command[0] not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command not allowed: {command[0]}")

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
        )

        return {
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
        }
