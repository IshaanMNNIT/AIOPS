import json
from ai_os.planner.base import BasePlanner
from ai_os.planner.plan import Plan
from ai_os.planner.validator import PlanValidator, PlanValidationError
from ai_os.planner.repair import PlanRepairer

class LLMPlanner(BasePlanner):
    def __init__(self, llm_client):
        self.llm = llm_client
        self.validator = PlanValidator()
        self.repairer = PlanRepairer()

    def plan(self, goal: str) -> Plan:
        prompt = self._build_prompt(goal)
        raw = self.llm.generate(prompt)

        try:
            data = json.loads(raw)
            plan = Plan(**data)
            plan = self.repairer.repair(plan)
            self.validator.validate(plan)
            return plan
        except Exception as e:
            raise PlanValidationError(str(e))

    def _build_prompt(self, goal: str) -> str:
      return f"""
    You are a deterministic planning engine.

    You MUST output ONLY valid JSON.
    Do NOT include explanations.
    Do NOT include markdown.
    Do NOT include text before or after JSON.

    The JSON MUST match this schema exactly:

    {{
      "goal": "{goal}",
      "steps": [
        {{
          "action": "command",
          "params": {{
            "command": ["ls"]
          }}
        }}
      ]
    }}

    Rules:
    - Only use action "command"
    - Only use commands: ls, pwd, echo
    - If you cannot create a valid plan, return EXACTLY this JSON:

    {{
      "goal": "{goal}",
      "steps": []
    }}

    Now produce the JSON plan.
    """

