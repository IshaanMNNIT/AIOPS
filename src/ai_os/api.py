# src/ai_os/api.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ai_os.model_manager import ModelManager
from ai_os.tasks.task_manager import TaskManager
from ai_os.executors.command_executor import CommandExecutor
from ai_os.planner.simple_planner import SimplePlanner
from ai_os.planner.executor import PlanExecutor
from ai_os.planner.llm_planner import LLMPlanner
from ai_os.llm.local import LocalLLMClient
from ai_os.planner.validator import PlanValidationError
from ai_os.security.policy import PolicyEngine, PolicyError
from ai_os.security.identity import Role
from ai_os.security.capabilities import Capability
from ai_os.llm.client import CloudLLMClient

local_llm = LocalLLMClient(model_path="models/llm/qwen2.5-1.5b-instruct.gguf")
model_manager = ModelManager()
task_manager = TaskManager()
command_executor = CommandExecutor()
planner = LLMPlanner(local_llm)
plan_executor = PlanExecutor(task_manager, command_executor)
policy_engine = PolicyEngine()
cloud_llm = None

class InferRequest(BaseModel):
    model: str
    prompt: str

class CommandTaskRequest(BaseModel):
    command: list[str]

class PlanRequest(BaseModel):
    goal: str

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
        role = Role.ADMIN  # only admins can do raw commands

        try:
            policy_engine.check(role, Capability.EXECUTE_COMMAND)
        except PolicyError as e:
            raise HTTPException(status_code=403, detail=str(e))

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

    @app.post("/v1/plan")
    def plan_and_execute(req: PlanRequest):
        role = Role.ADMIN  # auth comes later

        # 🔒 Authority: execution permission
        try:
            policy_engine.check(role, Capability.EXECUTE_COMMAND)
        except PolicyError as e:
            raise HTTPException(status_code=403, detail=str(e))

        # Planner selection
        active_planner = planner          # local LLM (default)
        use_cloud = False                 # Day 8: hardcoded OFF

        if use_cloud:
            # 🔒 Authority: cloud usage permission
            try:
                policy_engine.check(role, Capability.USE_CLOUD_LLM)
            except PolicyError as e:
                raise HTTPException(status_code=403, detail=str(e))

            global cloud_llm
            if cloud_llm is None:
                cloud_llm = CloudLLMClient()

            active_planner = LLMPlanner(cloud_llm)

        # Planning
        try:
            plan = active_planner.plan(req.goal)
        except PlanValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Execution (sandboxed)
        tasks = plan_executor.execute(plan)

        return {
            "goal": plan.goal,
            "steps": [s.dict() for s in plan.steps],
            "tasks": tasks,
        }





    return app


