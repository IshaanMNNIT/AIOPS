from ai_os.planner.plan import Plan


class PlanValidationError(Exception):
    pass


class PlanValidator:
    ALLOWED_ACTIONS = {"command"}
    ALLOWED_COMMANDS = {"ls", "pwd", "echo"}

    def validate(self, plan: Plan) -> None:
        if not plan.steps:
            raise PlanValidationError("Plan has no steps")

        for step in plan.steps:
            if step.action not in self.ALLOWED_ACTIONS:
                raise PlanValidationError(
                    f"Action not allowed: {step.action}"
                )

            if step.action == "command":
                params = step.params

                if "command" not in params:
                    raise PlanValidationError("Missing command")

                command = params["command"]

                # 🔒 ENFORCE LIST[str]
                if isinstance(command, str):
                    raise PlanValidationError(
                        "command must be a list, not a string"
                    )

                if not isinstance(command, list) or not command:
                    raise PlanValidationError(
                        "command must be a non-empty list"
                    )

                cmd_name = command[0]

                if cmd_name not in self.ALLOWED_COMMANDS:
                    raise PlanValidationError(
                        f"Command not allowed: {cmd_name}"
                    )
