from ai_os.planner.llm_planner import LLMPlanner
from ai_os.planner.validator import PlanValidationError
from ai_os.security.capabilities import Capability
from ai_os.security.policy import PolicyEngine , PolicyError

class PlannerDispatcher:

    def __init__(self , local_planner: LLMPlanner , cloud_planner: LLMPlanner | None , policy : PolicyEngine):
        self.local = local_planner
        self.cloud = cloud_planner
        self.policy = policy

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
        if not self.cloud:
            raise PlanValidationError("Local Planning failed and no cloud planner available")


        try:
            self.policy.check(role, Capability.USE_CLOUD_LLM)
        except PolicyError as e:
            raise PlanValidationError(f"Policy check failed for cloud planning: {str(e)}")
        
        return self.cloud.plan(goal)
