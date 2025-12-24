from ai_os.planner.llm_planner import LLMPlanner
from ai_os.planner.validator import PlanValidationError
from ai_os.security.capabilities import Capability
from ai_os.security.policy import PolicyEngine , PolicyError
from ai_os.planner.simple_planner import SimplePlanner
from ai_os.observability.logger import get_logger

logger = get_logger("planner.dispatcher")
class PlannerDispatcher:

    def __init__(self , local_planner: LLMPlanner , cloud_planner: LLMPlanner | None , policy : PolicyEngine):
        self.local = local_planner
        self.cloud = cloud_planner
        self.policy = policy
        self.simple = SimplePlanner()

    def plan(self , goal : str , role):
        """
        Local LLM
        ↓
        Repair
        ↓
        Validate
        ↓ (fails?)
        Retry Local (1x)
        ↓ (fails?)
        Policy check: USE_CLOUD_LLM
        ↓
        Cloud LLM (OpenRouter)
        ↓
        Repair
        ↓
        Validate
        ↓
        Execute
        """
        logger.info(f"Starting plan dispatch | goal='{goal}' | role={role}")

        logger.info("Attempting local planner (attempt 1)")

        try:
            return self.local.plan(goal)
        except PlanValidationError:
            pass
        
        logger.warning("Local planner failed, retrying (attempt 2)")

        try :
            return self.local.plan(goal)
        except PlanValidationError:
            pass
        
        logger.warning("Local planning failed, attempting cloud fallback")

        if self.cloud:
            try:
                self.policy.check(role, Capability.USE_CLOUD_LLM)
                return self.cloud.plan(goal)
            except PlanValidationError:
                pass
            except PolicyError as e:
                logger.error("Cloud Usage blocked by policy")
                raise PlanValidationError(str(e))

        # 4️⃣ Final deterministic fallback
        logger.warning("Falling back to deterministic SimplePlanner")

        try:
            return self.simple.plan(goal)
        except Exception:
            logger.error("All planning strategies failed")
            raise PlanValidationError(
                "Unable to create a safe execution plan"
            )
