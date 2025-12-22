from ai_os.planner.plan import Plan

class PlanRepairer:
    
    """
    Deterministic, auditable repair layer.
    Fixes common structural mistakes from LLM output.
    """

    def repair(self , plan : Plan) -> Plan:
        for step in plan.steps:

            if step.action == "command":
                cmd = step.params.get("command")

                # Normalize: "ls" -> ["ls"]
                if isinstance(cmd, str):
                    step.params["command"] = [cmd]
        return plan
