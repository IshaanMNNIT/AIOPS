# src/ai_os/llm/hybrid.py
class HybridLLMClient:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback

    def generate(self, prompt: str) -> str:
        try:
            return self.primary.generate(prompt)
        except Exception:
            return self.fallback.generate(prompt)
