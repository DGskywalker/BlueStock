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

@router.get("/peers/{group_name}")
def get_peer_group_percentiles(group_name: str):
    conn = get_db_conn()
    df_p = pd.read_sql("""
    SELECT p.*, c.ticker, c.company_name, c.sector
    FROM peer_percentiles p
    JOIN companies c ON p.company_id = c.company_id
    WHERE LOWER(p.peer_group_name) = ?
    """, conn, params=[group_name.lower()])
    conn.close()

    if df_p.empty:
        raise HTTPException(status_code=404, detail=f"Peer group '{group_name}' not found")
        
    return df_p.to_dict(orient="records")

@router.get("/companies/{ticker}/peers/compare")
def compare_company_peers(ticker: str):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id, ticker, company_name, sector FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    comp = df_c.iloc[0]
    sec = comp["sector"]

    df_sec_ratios = pd.read_sql("""
    SELECT c.ticker, c.company_name, r.*
    FROM financial_ratios r
    JOIN companies c ON r.company_id = c.company_id
    WHERE LOWER(c.sector) = ? AND r.year = 2024
    """, conn, params=[sec.lower()])
    conn.close()

    if df_sec_ratios.empty:
        raise HTTPException(status_code=404, detail="No sector peer records found")

    target_ratios = df_sec_ratios[df_sec_ratios["ticker"].str.upper() == ticker.upper()].to_dict(orient="records")
    target = target_ratios[0] if target_ratios else {}

    sector_averages = {
        "roe_avg": round(float(df_sec_ratios["return_on_equity_pct"].dropna().mean()), 2),
        "roce_avg": round(float(df_sec_ratios["return_on_capital_employed_pct"].dropna().mean()), 2),
        "npm_avg": round(float(df_sec_ratios["net_profit_margin_pct"].dropna().mean()), 2),
        "de_avg": round(float(df_sec_ratios["debt_to_equity"].dropna().mean()), 2),
        "fcf_avg": round(float(df_sec_ratios["free_cash_flow_cr"].dropna().mean()), 2),
        "rev_cagr_avg": round(float(df_sec_ratios["revenue_cagr_5yr"].dropna().mean()), 2),
        "pat_cagr_avg": round(float(df_sec_ratios["pat_cagr_5yr"].dropna().mean()), 2),
        "score_avg": round(float(df_sec_ratios["composite_quality_score"].dropna().mean()), 2)
    }

    return {
        "company": comp.to_dict(),
        "target_metrics": target,
        "peer_sector": sec,
        "sector_averages": sector_averages
    }
