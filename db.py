import sqlite3
import pandas as pd
from pathlib import Path

DB = Path(__file__).parent / "data" / "smartmart.db"

def run(sql, params=()):
    with sqlite3.connect(DB) as con:
        return pd.read_sql_query(sql, con, params=params)

def where(f):
    """Build a parameterised WHERE clause from the sidebar filters."""
    clauses, params = ["order_date BETWEEN ? AND ?"], [f["start"], f["end"]]
    for col, key in [("category", "categories"), ("region", "regions"), ("channel", "channels")]:
        if f[key]:
            clauses.append(f"{col} IN ({','.join('?' * len(f[key]))})")
            params += list(f[key])
    return " AND ".join(clauses), params