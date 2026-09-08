import os
import sqlite3
import pandas as pd
from typing import Optional
from fastapi import APIRouter, HTTPException
from src.screener.engine import ScreenerEngine

router = APIRouter()

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def get_db_conn():
    db_target = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    return sqlite3.connect(db_target)

@router.get("/screener")
def run_screener_api(
    min_roe: Optional[float] = None,
    max_de: Optional[float] = None,
    min_fcf: Optional[float] = None,
    sector: Optional[str] = None,
    min_rev_cagr_5yr: Optional[float] = None,
    min_pat_cagr_5yr: Optional[float] = None,
    max_pe: Optional[float] = None
):
    if min_roe is not None and min_roe < 0:
        raise HTTPException(status_code=400, detail="min_roe cannot be negative")
    if max_pe is not None and max_pe <= 0:
        raise HTTPException(status_code=400, detail="max_pe must be greater than zero")

    conn = get_db_conn()
    df_ratios = pd.read_sql("""
    SELECT c.company_id, c.ticker, c.company_name, c.sector, c.industry, r.*
    FROM financial_ratios r
    JOIN companies c ON r.company_id = c.company_id
    WHERE r.year = 2024
    """, conn)
    conn.close()

    screener = ScreenerEngine()
    active_filters = {}
    if min_roe is not None: active_filters["return_on_equity_pct_min"] = min_roe
    if max_de is not None: active_filters["debt_to_equity_max"] = max_de
    if min_fcf is not None: active_filters["free_cash_flow_cr_min"] = min_fcf
    if min_rev_cagr_5yr is not None: active_filters["revenue_cagr_5yr_min"] = min_rev_cagr_5yr
    if min_pat_cagr_5yr is not None: active_filters["pat_cagr_5yr_min"] = min_pat_cagr_5yr
    if max_pe is not None: active_filters["pe_ratio_max"] = max_pe

    df_filtered = screener.filter_universe(df_ratios, active_filters)
    if sector:
        df_filtered = df_filtered[df_filtered["sector"].str.lower() == sector.lower()]

    return {
        "match_count": len(df_filtered),
        "results": df_filtered.to_dict(orient="records")
    }
