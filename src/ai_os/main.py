# src/ai_os/main.py

import logging
import uvicorn
from ai_os.api import create_app
from ai_os.persistence.schema import init_db
from ai_os.config import Config , ConfigError
from ai_os.observability.logger import get_logger

try:
    Config.validate()
except ConfigError as e:
    raise RuntimeError(f"Configuration error:\n{e}")

init_db()

logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def main():
    app = create_app()
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()
