from ai_os.planner.plan import Plan, PlanStep
from ai_os.planner.base import BasePlanner

class SimplePlanner(BasePlanner):
    """
    Deterministic planner.
    Replaces LLM for now.
    """

    def plan(self, goal: str) -> Plan:
        g = goal.lower().strip()

        if "list" in g and "files" in g:
            return Plan(
                goal=goal,
                steps=[
                    PlanStep
                    (
                        action="command",
                        params={"command": ["ls"]},
                    )
                ]
            )
        
        if "working directory" in g or "pwd" in g:
            return Plan(
                goal=goal,
                steps=[
                    PlanStep
                    (
                        action="command",
                        params={"command": ["pwd"]},
                    )
                ]
            )
        
        if g.startswith("echo "):
            msg = goal[5:].strip()
            return Plan(
                goal=goal,
                steps=[
                    PlanStep(
                        action="command",
                        params={"command": ["echo", msg]},
                    )
                ]
            )

        raise ValueError("Simple Planner cannot handle this goal")