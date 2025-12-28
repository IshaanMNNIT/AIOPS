import time
from ai_os.planner.llm_planner import LLMPlanner
from ai_os.planner.validator import PlanValidationError
from ai_os.security.capabilities import Capability
from ai_os.security.policy import PolicyEngine, PolicyError
from ai_os.planner.simple_planner import SimplePlanner
from ai_os.observability.logger import get_logger
from ai_os.persistence.db import get_conn

logger = get_logger("planner.dispatcher")

FORBIDDEN_KEYWORDS = [
    "rm",
    "delete",
    "shutdown",
    "format",
    "kill",
]


class PlannerDispatcher:
    def __init__(
        self,
        local_planner: LLMPlanner,
        cloud_planner: LLMPlanner | None,
        policy: PolicyEngine,
    ):
        self.local = local_planner
        self.cloud = cloud_planner
        self.policy = policy
        self.simple = SimplePlanner()

    def _persist_plan(self, goal: str, planner_used: str):
        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO plans (goal, planner_used, created_at)
            VALUES (?, ?, ?)
            """,
            (goal, planner_used, time.time()),
        )

        conn.commit()
        conn.close()

    def _check_goal_safety(self, goal: str):
        if any(word in goal.lower() for word in FORBIDDEN_KEYWORDS):
            raise PlanValidationError("Unsafe goal detected")

    def plan(self, goal: str, role):
        """
        Planning strategy:

        Local LLM (x2)
          ↓
        Cloud LLM (if allowed)
          ↓
        Deterministic SimplePlanner
        """

        logger.info(f"Starting plan dispatch | goal='{goal}' | role={role}")

        # 🔒 Day 17: Fail fast on unsafe intent
        self._check_goal_safety(goal)

        # 1️⃣ Local attempt 1
        logger.info("Attempting local planner (attempt 1)")
        try:
            plan = self.local.plan(goal)
            self._persist_plan(goal, "local")
            return plan
        except PlanValidationError:
            pass

        # 2️⃣ Local retry
        logger.warning("Local planner failed, retrying (attempt 2)")
        try:
            plan = self.local.plan(goal)
            self._persist_plan(goal, "local")
            return plan
        except PlanValidationError:
            pass

        # 3️⃣ Cloud fallback
        logger.warning("Local planning failed, attempting cloud fallback")
        if self.cloud:
            try:
                self.policy.check(role, Capability.USE_CLOUD_LLM)
                plan = self.cloud.plan(goal)
                self._persist_plan(goal, "cloud")
                return plan
            except PolicyError as e:
                logger.error("Cloud usage blocked by policy")
                raise PlanValidationError(str(e))
            except PlanValidationError:
                pass

        # 4️⃣ Deterministic fallback
        logger.warning("Falling back to deterministic SimplePlanner")
        try:
            plan = self.simple.plan(goal)
            self._persist_plan(goal, "simple")
            return plan
        except Exception:
            logger.error("All planning strategies failed")
            raise PlanValidationError("Unable to create a safe execution plan")
