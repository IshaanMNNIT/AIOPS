# src/ai_os/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_os.model_manager import ModelManager
from ai_os.tasks.task_manager import TaskManager
from ai_os.executors.command_executor import CommandExecutor

model_manager = ModelManager()
task_manager = TaskManager()
command_executor = CommandExecutor()

class InferRequest(BaseModel):
    model: str
    prompt: str

class CommandTaskRequest(BaseModel):
    command: list[str]

def create_app() -> FastAPI:
    app = FastAPI(
        title="AI OS Daemon",
        version="0.1.0"
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/v1/models")
    def list_models():
        return model_manager.list_models()

    @app.post("/v1/infer")
    def infer(req: InferRequest):
        if req.model not in model_manager.list_models():
            raise HTTPException(status_code=404, detail="Model not found")
        try:
            return {"result": model_manager.infer(req.model, req.prompt)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        
    @app.post("/v1/tasks/command")
    def run_command(req: CommandTaskRequest):
        task = task_manager.create_task("command", req.dict())

        try:
            task.status = "running"
            task.result = command_executor.run(req.command)
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.error = str(e)

        task_manager.update_task(task)
        return task

    @app.get("/v1/tasks/{task_id}")
    def get_task(task_id: str):
        return task_manager.get_task(task_id)

    return app


