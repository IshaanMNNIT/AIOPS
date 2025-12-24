from ai_os.security.capabilities import Capability 
from ai_os.security.identity import Role
from ai_os.observability.logger import get_logger
logger = get_logger("security.policy")

ROLE_CAPABILITIES = {
    Role.ADMIN: {
        Capability.EXECUTE_COMMAND,
        Capability.READ_FILES,
        Capability.WRITE_FILES,
        Capability.USE_CLOUD_LLM,
    },
    Role.USER: {
        Capability.EXECUTE_COMMAND,
        Capability.READ_FILES,
    },
    Role.SYSTEM: {
        Capability.EXECUTE_COMMAND,
    },
}

class PolicyError(Exception):
    pass


class PolicyEngine:
    def check(self, role: Role, capability: Capability):

        logger.info(f"Checking policy for role={role}, capability={capability}")

        allowed = ROLE_CAPABILITIES.get(role, set())

        if capability not in allowed:

            logger.warning(f"Policy check failed for role={role}, capability={capability}")
            
            raise PolicyError(
                f"Role '{role}' not allowed to perform '{capability}'"
            )