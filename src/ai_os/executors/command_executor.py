import subprocess
import time
from typing import List, Dict

from ai_os.observability.logger import get_logger

logger = get_logger("executors.command")


class CommandExecutionError(Exception):
    pass


class CommandExecutor:
    """
    Secure command executor.
    - Strict allow-list
    - No shell
    - Argument validation
    - Timeout enforced
    """

    # Command → allowed args
    ALLOWED_COMMANDS = {
        "ls": [],            # no args allowed
        "pwd": [],           # no args allowed
        "echo": ["*"],       # echo can take any args
    }

    TIMEOUT_SECONDS = 3

    def run(self, command: List[str]) -> Dict:
        if not command or not isinstance(command, list):
            raise CommandExecutionError("Command must be a list")

        cmd = command[0]
        args = command[1:]

        logger.info(f"Executing command: {' '.join(command)}")

        # Command allow-list
        if cmd not in self.ALLOWED_COMMANDS:
            raise CommandExecutionError(f"Command not allowed: {cmd}")

        # Argument validation
        allowed_args = self.ALLOWED_COMMANDS[cmd]
        if allowed_args != ["*"] and args:
            raise CommandExecutionError(
                f"Arguments not allowed for command: {cmd}"
            )

        start = time.time()

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
            )

        except subprocess.TimeoutExpired:
            logger.warning(f"Command timed out: {' '.join(command)}")
            raise CommandExecutionError("Command execution timed out")

        duration = time.time() - start

        logger.info(
            f"Command executed | cmd={cmd} | "
            f"returncode={completed.returncode} | "
            f"duration_ms={int(duration * 1000)}"
        )

        return {
            "stdout": completed.stdout.strip(),
            "stderr": completed.stderr.strip(),
            "returncode": completed.returncode,
            "duration_ms": int(duration * 1000),
        }
