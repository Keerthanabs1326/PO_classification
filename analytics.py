import sqlite3
import pandas as pd

DB_PATH = "po_data.db"

def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM classifications", conn)
    conn.close()
    return df

def spend_by_category(df):
    return df.groupby(["L1", "L2"]).size().reset_index(name="count")

def not_sure_percentage(df):
    total = len(df)
    not_sure = len(df[df["L1"] == "Not sure"])
    return (not_sure / total * 100) if total > 0 else 0
