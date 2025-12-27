import httpx
from ai_os.config import Config , ConfigError


class CloudLLMClient:
    """
    OpenRouter client (DeepSeek model).
    Used ONLY for planning.
    """

    def __init__(self , api_key : str , base_url : str , model : str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a planning engine. "
                        "Return ONLY valid JSON. "
                        "No explanations. No markdown."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            "temperature": 0.1,
            "max_tokens": 512,
        }

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            timeout=15.0,
        )

        response.raise_for_status()

        data = response.json()

        return data["choices"][0]["message"]["content"]
