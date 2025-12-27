# src/ai_os/main.py

import logging
import uvicorn
from ai_os.api import create_app
from config.settings import settings    
from ai_os.persistence.schema import init_db
init_db()

logging.basicConfig(
    level=settings.log_level,
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
