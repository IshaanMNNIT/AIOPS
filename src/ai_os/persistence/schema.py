from ai_os.persistence.db import get_conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        type TEXT,
        status TEXT,
        payload TEXT,
        result TEXT,
        error TEXT,
        created_at REAL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal TEXT,
        planner_used TEXT,
        created_at REAL
    )
    """)

    conn.commit()
    conn.close()
