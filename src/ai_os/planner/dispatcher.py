from ai_os.planner.llm_planner import LLMPlanner
from ai_os.planner.validator import PlanValidationError
from ai_os.security.capabilities import Capability
from ai_os.security.policy import PolicyEngine , PolicyError
from ai_os.planner.simple_planner import SimplePlanner
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
        print("PlannerDispatcher: Starting plan dispatch")

        try:
            return self.local.plan(goal)
        except PlanValidationError:
            pass

        try :
            return self.local.plan(goal)
        except PlanValidationError:
            pass
        
        print("☁️ Attempting cloud fallback")
        if self.cloud:
            try:
                self.policy.check(role, Capability.USE_CLOUD_LLM)
                return self.cloud.plan(goal)
            except PlanValidationError:
                pass
            except PolicyError as e:
                raise PlanValidationError(str(e))

        # 4️⃣ Final deterministic fallback
        try:
            return self.simple.plan(goal)
        except Exception:
            raise PlanValidationError(
                "Unable to create a safe execution plan"
            )
