from typing import Dict
import time
import json

from ai_os.tasks.task import Task
from ai_os.persistence.db import get_conn


class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self._load_tasks_from_db()

    # ----------------------------
    # Internal: load persisted tasks
    # ----------------------------
    def _load_tasks_from_db(self):
        conn = get_conn()
        cur = conn.cursor()
        try :
            cur.execute(
                """
                SELECT id, type, status, payload, result, error
                FROM tasks
                """
            )
        except Exception as e:
            conn.close()
            return 

        rows = cur.fetchall()
        for row in rows:
            task = Task(
                id=row[0],
                type=row[1],
                payload=json.loads(row[3]),
            )
            task.status = row[2]
            task.result = json.loads(row[4]) if row[4] else None
            task.error = row[5]

            self.tasks[task.id] = task

        conn.close()

    # ----------------------------
    # Create task (write-through)
    # ----------------------------
    def create_task(self, task_type: str, payload: Dict) -> Task:
        task = Task(type=task_type, payload=payload)
        self.tasks[task.id] = task

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO tasks (id, type, status, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task.id,
                task.type,
                task.status,
                json.dumps(task.payload),
                time.time(),
            ),
        )

        conn.commit()
        conn.close()

        return task

    # ----------------------------
    # Read task
    # ----------------------------
    def get_task(self, task_id: str) -> Task:
        return self.tasks[task_id]

    # ----------------------------
    # Update task (write-through)
    # ----------------------------
    def update_task(self, task: Task):
        self.tasks[task.id] = task

        conn = get_conn()
        cur = conn.cursor()

        cur.execute(
            """
            UPDATE tasks
            SET status = ?, result = ?, error = ?
            WHERE id = ?
            """,
            (
                task.status,
                json.dumps(task.result) if task.result else None,
                task.error,
                task.id,
            ),
        )

        conn.commit()
        conn.close()
