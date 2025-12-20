import json
from ai_os.planner.base import BasePlanner
from ai_os.planner.plan import Plan
from ai_os.planner.validator import PlanValidator, PlanValidationError


class LLMPlanner(BasePlanner):
    def __init__(self, llm_client):
        self.llm = llm_client
        self.validator = PlanValidator()

    def plan(self, goal: str) -> Plan:
        prompt = self._build_prompt(goal)
        raw = self.llm.generate(prompt)

        try:
            data = json.loads(raw)
            plan = Plan(**data)
            self.validator.validate(plan)
            return plan
        except Exception as e:
            raise PlanValidationError(str(e))

    def _build_prompt(self, goal: str) -> str:
        return f"""
You are a planning engine.

Return ONLY valid JSON matching this schema:

{{
  "goal": string,
  "steps": [
    {{
      "action": "command",
      "params": {{
        "command": ["ls" | "pwd" | "echo", "..."]
      }}
    }}
  ]
}}

Goal: {goal}
"""
