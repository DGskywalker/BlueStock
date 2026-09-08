import os
import sqlite3
import pandas as pd
import numpy as np
from fastapi import APIRouter

router = APIRouter()

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def get_db_conn():
    db_target = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    return sqlite3.connect(db_target)

@router.get("/portfolio/stats")
def get_portfolio_stats():
    conn = get_db_conn()
    df_r = pd.read_sql("SELECT * FROM financial_ratios WHERE year = 2024", conn)
    conn.close()

    kpi_cols = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                "debt_to_equity", "operating_profit_margin_pct", "interest_coverage",
                "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr", "pe_ratio"]

    stats = []
    for col in kpi_cols:
        if col in df_r.columns:
            s = df_r[col].dropna()
            if not s.empty:
                stats.append({
                    "metric": col,
                    "P10": round(float(np.percentile(s, 10)), 2),
                    "P25": round(float(np.percentile(s, 25)), 2),
                    "P50_Median": round(float(np.median(s)), 2),
                    "P75": round(float(np.percentile(s, 75)), 2),
                    "P90": round(float(np.percentile(s, 90)), 2),
                    "Mean": round(float(s.mean()), 2),
                    "StdDev": round(float(s.std()), 2)
                })

    return {
        "company_universe_count": df_r["company_id"].nunique(),
        "year": 2024,
        "percentiles": stats
    }
