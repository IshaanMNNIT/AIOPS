import time
from fastapi import Request
from ai_os.observability.logger import get_logger

logger = get_logger("timing")


async def timing_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path} completed in {duration:.2f}ms"
    )

    response.headers["X-Response-Time-ms"] = f"{duration:.2f}"
    return response
