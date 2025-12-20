from ai_os.planner.plan import Plan, PlanStep
from ai_os.planner.base import BasePlanner

class SimplePlanner(BasePlanner):
    """
    Deterministic planner.
    Replaces LLM for now.
    """

    def plan(self, goal: str) -> Plan:
        goal_lower = goal.lower()

        if "list files" in goal_lower:
            return Plan(
                goal=goal,
                steps=[
                    PlanStep(
                        action="command",
                        params={"command": ["ls"]},
                    )
                ],
            )

        if "where am i" in goal_lower:
            return Plan(
                goal=goal,
                steps=[
                    PlanStep(
                        action="command",
                        params={"command": ["pwd"]},
                    )
                ],
            )

        # Default fallback
        return Plan(
            goal=goal,
            steps=[
                PlanStep(
                    action="command",
                    params={"command": ["echo", "No plan available"]},
                )
            ],
        )
