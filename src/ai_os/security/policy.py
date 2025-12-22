from ai_os.security.capabilities import Capability 
from ai_os.security.identity import Role

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
        allowed = ROLE_CAPABILITIES.get(role, set())
        if capability not in allowed:
            raise PolicyError(
                f"Role '{role}' not allowed to perform '{capability}'"
            )