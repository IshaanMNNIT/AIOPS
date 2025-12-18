# config/settings.py

from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    env: str = os.getenv("AIOS_ENV", "dev")
    log_level: str = os.getenv("AIOS_LOG_LEVEL", "INFO")

    default_device: str = os.getenv("AIOS_DEFAULT_DEVICE", "cpu")
    default_model: str = os.getenv("AIOS_DEFAULT_MODEL", "")


settings = Settings()
