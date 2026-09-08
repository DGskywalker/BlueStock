import time
import os
import sqlite3
from fastapi import APIRouter

router = APIRouter()
START_TIME = time.time()

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

@router.get("/health")
def get_health():
    db_target = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    counts = {}
    if os.path.exists(db_target):
        conn = sqlite3.connect(db_target)
        cur = conn.cursor()
        tables = ["companies", "profitandloss", "balancesheet", "cashflow", "financial_ratios", "analysis", "documents", "prosandcons", "sectors", "stock_prices"]
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                counts[t] = cur.fetchone()[0]
            except Exception:
                counts[t] = 0
        conn.close()
        
    return {
        "status": "ok",
        "version": "1.0.0",
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "db_row_counts": counts
    }
