import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    pass


class Config:
    # Environment
    ENV = os.getenv("AIOS_ENV", "dev")
    LOG_LEVEL = os.getenv("AIOS_LOG_LEVEL", "INFO")

    # Storage
    DATA_DIR = Path(os.getenv("AIOS_DATA_DIR", "data"))
    DB_PATH = DATA_DIR / "ai_os.db"

    # Defaults
    DEFAULT_DEVICE = os.getenv("AIOS_DEFAULT_DEVICE", "cpu")
    LOCAL_LLM_PATH = os.getenv("AIOS_LOCAL_LLM_PATH")

    # OpenRouter / Cloud LLM
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv(
        "OPENROUTER_BASE_URL",
        "https://openrouter.ai/api/v1"
    )
    OPENROUTER_MODEL = os.getenv(
        "OPENROUTER_MODEL",
        "deepseek/deepseek-v3.2"
    )

    ENABLE_CLOUD_LLM = bool(OPENROUTER_API_KEY)

    @classmethod
    def validate(cls):
        errors = []

        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)

        if not cls.LOCAL_LLM_PATH:
            errors.append("AIOS_LOCAL_LLM_PATH is not set")

        elif not Path(cls.LOCAL_LLM_PATH).exists():
            errors.append(f"AIOS_LOCAL_LLM_PATH '{cls.LOCAL_LLM_PATH}' does not exist")
            
        if cls.ENABLE_CLOUD_LLM:
            if not cls.OPENROUTER_API_KEY:
                errors.append("OPENROUTER_API_KEY is missing")
            if not cls.OPENROUTER_MODEL:
                errors.append("OPENROUTER_MODEL is missing")

        if errors:
            raise ConfigError("\n".join(errors))
