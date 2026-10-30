"""Load the project's CSV datasets into a local SQLite database for SQL practice."""
from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
DB_PATH = ROOT / "logistics_demo.db"
TABLES = ["shipments", "transporters", "warehouses", "warehouse_operations", "inventory", "orders", "products", "cost_benchmarks"]

with sqlite3.connect(DB_PATH) as conn:
    for table in TABLES:
        frame = pd.read_csv(DATA / f"{table}.csv")
        frame.to_sql(table, conn, if_exists="replace", index=False)
print(f"Loaded {len(TABLES)} tables into {DB_PATH}")
print("Open sql/queries.sql in a SQLite client, or run queries against logistics_demo.db.")
