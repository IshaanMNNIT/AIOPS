from typing import Dict
from ai_os.tasks.task import Task, TaskStatus


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}

    def create_task(self, task_type: str, payload: Dict) -> Task:
        task = Task(type=task_type, payload=payload)
        self.tasks[task.id] = task
        return task

    def get_task(self, task_id: str) -> Task:
        return self.tasks[task_id]

    def update_task(self, task: Task):
        self.tasks[task.id] = task
