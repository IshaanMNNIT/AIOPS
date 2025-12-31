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

    def _persist_plan(self, goal: str, planner_used: str, duration_ms: float):
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

        logger.info(
            f"Plan persisted | planner={planner_used} | duration={duration_ms:.2f}ms"
        )

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

        # 🔒 Fail fast on unsafe intent
        self._check_goal_safety(goal)

        # 1️⃣ Local attempt 1
        logger.info("Attempting local planner (attempt 1)")
        start = time.time()
        try:
            plan = self.local.plan(goal)
            duration = (time.time() - start) * 1000
            logger.info(f"Local planner succeeded in {duration:.2f}ms")
            self._persist_plan(goal, "local", duration)
            return plan
        except PlanValidationError:
            duration = (time.time() - start) * 1000
            logger.warning(f"Local planner failed in {duration:.2f}ms")

        # 2️⃣ Local retry
        logger.warning("Retrying local planner (attempt 2)")
        start = time.time()
        try:
            plan = self.local.plan(goal)
            duration = (time.time() - start) * 1000
            logger.info(f"Local retry succeeded in {duration:.2f}ms")
            self._persist_plan(goal, "local", duration)
            return plan
        except PlanValidationError:
            duration = (time.time() - start) * 1000
            logger.warning(f"Local retry failed in {duration:.2f}ms")

        # 3️⃣ Cloud fallback
        logger.warning("Attempting cloud planner fallback")
        if self.cloud:
            try:
                self.policy.check(role, Capability.USE_CLOUD_LLM)
                start = time.time()
                plan = self.cloud.plan(goal)
                duration = (time.time() - start) * 1000
                logger.info(f"Cloud planner succeeded in {duration:.2f}ms")
                self._persist_plan(goal, "cloud", duration)
                return plan
            except PolicyError as e:
                logger.error("Cloud usage blocked by policy")
                raise PlanValidationError(str(e))
            except PlanValidationError:
                duration = (time.time() - start) * 1000
                logger.warning(f"Cloud planner failed in {duration:.2f}ms")

        # 4️⃣ Deterministic fallback
        logger.warning("Falling back to deterministic SimplePlanner")
        start = time.time()
        try:
            plan = self.simple.plan(goal)
            duration = (time.time() - start) * 1000
            logger.info(f"Simple planner succeeded in {duration:.2f}ms")
            self._persist_plan(goal, "simple", duration)
            return plan
        except Exception:
            duration = (time.time() - start) * 1000
            logger.error(
                f"All planning strategies failed | total_time={duration:.2f}ms"
            )
            raise PlanValidationError("Unable to create a safe execution plan")
