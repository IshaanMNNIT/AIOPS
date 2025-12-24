import subprocess
from typing import List, Dict
from ai_os.observability.logger import get_logger
import time
logger = get_logger("executors.command")

class CommandExecutor:
    ALLOWED_COMMANDS = {"ls", "pwd", "echo"}

    def run(self, command: List[str]) -> Dict:
        start = time.time()
        logger.info(f"Executing command: {' '.join(command)}")

        if command[0] not in self.ALLOWED_COMMANDS:
            raise ValueError(f"Command not allowed: {command[0]}")

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=5,
        )

        duration = time.time() - start
        logger.info(
            f"Command executed in {duration:.2f}s | returncode={completed.returncode}"
        )
        
        return {
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
        }
