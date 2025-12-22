from ai_os.config import settings

class CloudLLMClient:
    """Open Router LLM Client"""

    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError("OPENROUTER_API_KEY not configured in environment variables.")
        
        self.base_url = settings.OPENROUTER_BASE_URL
        self.model = settings.OPENROUTER_MODEL

    def generate(Self , prompt: str) -> str:
        raise NotImplementedError(
            "Cloud LLM is disabled until Day 11"
        )