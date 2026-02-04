import sqlite3
from datetime import datetime

DB_PATH = "po_data.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            po_description TEXT,
            supplier TEXT,
            L1 TEXT,
            L2 TEXT,
            L3 TEXT,
            confidence REAL,
            taxonomy_version TEXT,
            action TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_record(po_description, supplier, result, action):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        INSERT INTO classifications VALUES (NULL,?,?,?,?,?,?,?,?,?)
    """, (
        datetime.utcnow().isoformat(),
        po_description,
        supplier,
        result["L1"],
        result["L2"],
        result["L3"],
        result["confidence"],
        result["taxonomy_version"],
        action
    ))

    conn.commit()
    conn.close()
