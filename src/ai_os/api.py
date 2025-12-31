from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from ai_os.observability.timing import timing_middleware
from ai_os.model_manager import ModelManager
from ai_os.tasks.task_manager import TaskManager
from ai_os.executors.command_executor import CommandExecutor
from ai_os.planner.executor import PlanExecutor
from ai_os.planner.llm_planner import LLMPlanner
from ai_os.planner.validator import PlanValidationError
from ai_os.security.policy import PolicyEngine, PolicyError
from ai_os.security.capabilities import Capability
from ai_os.security.auth import resolve_request_context
from ai_os.security.rate_limit import RateLimiter, RateLimitError
from ai_os.llm.local import LocalLLMClient
from ai_os.llm.client import CloudLLMClient
from ai_os.planner.dispatcher import PlannerDispatcher
from ai_os.config import Config

# ---- Globals ----

rate_limiter = RateLimiter(max_requests=10, window_seconds=60)

local_llm = LocalLLMClient(model_path=Config.LOCAL_LLM_PATH)
model_manager = ModelManager()
task_manager = TaskManager()
command_executor = CommandExecutor()

plan_executor = PlanExecutor(task_manager, command_executor)
policy_engine = PolicyEngine()

local_planner = LLMPlanner(local_llm)

cloud_planner = None
if Config.ENABLE_CLOUD_LLM:
    cloud_llm = CloudLLMClient(
        api_key=Config.OPENROUTER_API_KEY,
        base_url=Config.OPENROUTER_BASE_URL,
        model=Config.OPENROUTER_MODEL,
    )
    cloud_planner = LLMPlanner(cloud_llm)

dispatcher = PlannerDispatcher(
    local_planner=local_planner,
    cloud_planner=cloud_planner,
    policy=policy_engine,
)

# ---- Schemas ----

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
        version="0.1.0",
    )

    app.middleware("http")(timing_middleware)

    @app.get("/health")
    def health():
        return {
            "status": "ok",
            "env": Config.ENV,
            "cloud_enabled": Config.ENABLE_CLOUD_LLM,
        }

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
    def run_command(req: CommandTaskRequest, request: Request):
        ctx = resolve_request_context(request)
        rate_key = f"{request.client.host}:{ctx.role}"

        # 🚦 Day 17: rate limiting
        try:
            rate_limiter.check(rate_key)
        except RateLimitError as e:
            raise HTTPException(status_code=429, detail=str(e))

        # 🔒 Authorization
        try:
            policy_engine.check(ctx.role, Capability.EXECUTE_COMMAND)
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
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "Command Failed",
                        "message": str(e),
                    }
                },
            )

        task_manager.update_task(task)
        return task

    @app.get("/v1/tasks/{task_id}")
    def get_task(task_id: str):
        return task_manager.get_task(task_id)

    @app.post("/v1/plan")
    def plan_and_execute(req: PlanRequest, request: Request):
        ctx = resolve_request_context(request)
        rate_key = f"{request.client.host}:{ctx.role}"

        # 🚦 Day 17: rate limiting
        try:
            rate_limiter.check(rate_key)
        except RateLimitError as e:
            raise HTTPException(status_code=429, detail=str(e))

        # 🔒 Authorization
        try:
            policy_engine.check(ctx.role, Capability.EXECUTE_COMMAND)
        except PolicyError as e:
            raise HTTPException(status_code=403, detail=str(e))

        try:
            plan = dispatcher.plan(req.goal, ctx.role)
        except PlanValidationError as e:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "code": "Plan Failed",
                        "message": str(e),
                    }
                },
            )

        tasks = plan_executor.execute(plan)

        return {
            "goal": plan.goal,
            "steps": [s.dict() for s in plan.steps],
            "tasks": tasks,
        }

    return app
