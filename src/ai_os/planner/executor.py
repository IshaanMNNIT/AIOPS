from ai_os.tasks.task_manager import TaskManager
from ai_os.executors.command_executor import CommandExecutor


class PlanExecutor:
    def __init__(self, task_manager: TaskManager, command_executor: CommandExecutor):
        self.task_manager = task_manager
        self.command_executor = command_executor

    def execute(self, plan):
        results = []

        for step in plan.steps:
            if step.action == "command":
                task = self.task_manager.create_task("command", step.params)
                try:
                    task.status = "running"
                    task.result = self.command_executor.run(step.params["command"])
                    task.status = "completed"
                except Exception as e:
                    task.status = "failed"
                    task.error = str(e)

                self.task_manager.update_task(task)
                results.append(task)

            else:
                raise ValueError(f"Unsupported action: {step.action}")

        return results
