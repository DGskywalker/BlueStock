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

@router.get("/sectors")
def list_sectors():
    conn = get_db_conn()
    df_merged = pd.read_sql("""
    SELECT c.sector, r.return_on_equity_pct, r.pe_ratio, r.debt_to_equity
    FROM companies c
    LEFT JOIN financial_ratios r ON c.company_id = r.company_id AND r.year = 2024
    """, conn)
    conn.close()

    result = []
    for sector_name, grp in df_merged.groupby("sector"):
        result.append({
            "sector": sector_name,
            "company_count": len(grp),
            "median_roe": round(float(grp["return_on_equity_pct"].dropna().median()), 2) if not grp["return_on_equity_pct"].dropna().empty else 0.0,
            "median_pe": round(float(grp["pe_ratio"].dropna().median()), 2) if not grp["pe_ratio"].dropna().empty else 0.0,
            "median_de": round(float(grp["debt_to_equity"].dropna().median()), 2) if not grp["debt_to_equity"].dropna().empty else 0.0
        })
    return result

@router.get("/sectors/{sector}/companies")
def get_sector_companies(sector: str):
    conn = get_db_conn()
    df_merged = pd.read_sql("""
    SELECT c.company_id, c.ticker, c.company_name, c.sector, c.industry, r.*
    FROM companies c
    LEFT JOIN financial_ratios r ON c.company_id = r.company_id AND r.year = 2024
    WHERE LOWER(c.sector) = ?
    """, conn, params=[sector.lower()])
    conn.close()

    if df_merged.empty:
        raise HTTPException(status_code=404, detail=f"Sector '{sector}' not found")
        
    return df_merged.to_dict(orient="records")
