import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "employees.db"

def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emp_id TEXT UNIQUE,
        name TEXT,
        department TEXT,
        folder_path TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_id INTEGER,
        date TEXT,
        time TEXT,
        mode TEXT,
        camera TEXT
    )
    """)

    con.commit()
    con.close()
