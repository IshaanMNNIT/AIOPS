from ai_os.planner.plan import Plan


class PlanValidationError(Exception):
    pass


class PlanValidator:
    ALLOWED_ACTIONS = {"command"}

    def validate(self, plan: Plan) -> None:
        if not plan.steps:
            raise PlanValidationError("Plan has no steps")

        for step in plan.steps:
            if step.action not in self.ALLOWED_ACTIONS:
                raise PlanValidationError(
                    f"Action not allowed: {step.action}"
                )

            if step.action == "command":
                if "command" not in step.params:
                    raise PlanValidationError("Missing command params")
