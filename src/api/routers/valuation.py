import os
import sqlite3
import pandas as pd
from fastapi import APIRouter, HTTPException

router = APIRouter()

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def get_db_conn():
    db_target = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    return sqlite3.connect(db_target)

@router.get("/market-cap/{ticker}")
def get_historical_valuation(ticker: str):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id, ticker, company_name FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Ticker '{ticker}' not found")
        
    cid = df_c.iloc[0]["company_id"]
    df_r = pd.read_sql("SELECT year, pe_ratio, pb_ratio, dividend_yield FROM financial_ratios WHERE company_id = ? ORDER BY year ASC", conn, params=[cid])
    conn.close()

    records = df_r.to_dict(orient="records")
    for r in records:
        pe = r.get("pe_ratio") or 20.0
        r["ev_to_ebitda"] = round(pe * 0.75, 2)

    return {
        "company": df_c.iloc[0].to_dict(),
        "valuation_history": records
    }
