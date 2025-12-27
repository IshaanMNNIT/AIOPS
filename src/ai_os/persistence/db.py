import sqlite3
from pathlib import Path

DB_PATH = Path("data/ai_os.db")
DB_PATH.parent.mkdir(parents = True , exist_ok=True)

def get_conn():
    return sqlite3.connect(DB_PATH)