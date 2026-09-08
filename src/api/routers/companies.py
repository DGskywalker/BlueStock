import os
import sqlite3
import pandas as pd
from typing import Optional
from fastapi import APIRouter, HTTPException, Response

router = APIRouter()

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def get_db_conn():
    db_target = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    return sqlite3.connect(db_target)

@router.get("/companies")
def list_companies(sector: Optional[str] = None, search: Optional[str] = None):
    conn = get_db_conn()
    query = "SELECT * FROM companies WHERE 1=1"
    params = []
    if sector:
        query += " AND sector = ?"
        params.append(sector)
    if search:
        query += " AND (ticker LIKE ? OR company_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY company_name ASC"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df.to_dict(orient="records")

@router.get("/companies/{ticker}")
def get_company_profile(ticker: str):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT * FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Company with ticker '{ticker}' not found")
        
    comp = df_c.iloc[0].to_dict()
    df_r = pd.read_sql("SELECT * FROM financial_ratios WHERE company_id = ? ORDER BY year DESC LIMIT 1", conn, params=[comp["company_id"]])
    conn.close()
    
    comp["latest_ratios"] = df_r.iloc[0].to_dict() if not df_r.empty else {}
    return comp

@router.get("/companies/{ticker}/pl")
def get_company_pl(ticker: str, from_year: Optional[int] = None, to_year: Optional[int] = None):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    cid = df_c.iloc[0]["company_id"]
    query = "SELECT * FROM profitandloss WHERE company_id = ?"
    params = [cid]
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
    query += " ORDER BY year ASC"
    df_pl = pd.read_sql(query, conn, params=params)
    conn.close()
    return df_pl.to_dict(orient="records")

@router.get("/companies/{ticker}/bs")
def get_company_bs(ticker: str, from_year: Optional[int] = None, to_year: Optional[int] = None):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    cid = df_c.iloc[0]["company_id"]
    query = "SELECT * FROM balancesheet WHERE company_id = ?"
    params = [cid]
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
    query += " ORDER BY year ASC"
    df_bs = pd.read_sql(query, conn, params=params)
    conn.close()
    return df_bs.to_dict(orient="records")

@router.get("/companies/{ticker}/cashflow")
def get_company_cf(ticker: str, from_year: Optional[int] = None, to_year: Optional[int] = None):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    cid = df_c.iloc[0]["company_id"]
    query = "SELECT * FROM cashflow WHERE company_id = ?"
    params = [cid]
    if from_year:
        query += " AND year >= ?"
        params.append(from_year)
    if to_year:
        query += " AND year <= ?"
        params.append(to_year)
    query += " ORDER BY year ASC"
    df_cf = pd.read_sql(query, conn, params=params)
    conn.close()
    return df_cf.to_dict(orient="records")

@router.get("/companies/{ticker}/ratios")
def get_company_ratios(ticker: str, year: Optional[int] = None):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    cid = df_c.iloc[0]["company_id"]
    query = "SELECT * FROM financial_ratios WHERE company_id = ?"
    params = [cid]
    if year:
        query += " AND year = ?"
        params.append(year)
    query += " ORDER BY year ASC"
    df_r = pd.read_sql(query, conn, params=params)
    conn.close()
    return df_r.to_dict(orient="records")

@router.get("/companies/{ticker}/tearsheet")
def download_company_tearsheet(ticker: str):
    pdf_path = f"reports/tearsheets/{ticker.upper()}_tearsheet.pdf"
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail=f"Tearsheet PDF for '{ticker}' not found")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename={ticker.upper()}_tearsheet.pdf"})

@router.get("/companies/{ticker}/documents")
def get_company_documents(ticker: str):
    conn = get_db_conn()
    df_c = pd.read_sql("SELECT company_id FROM companies WHERE UPPER(ticker) = ?", conn, params=[ticker.upper()])
    if df_c.empty:
        conn.close()
        raise HTTPException(status_code=404, detail="Company not found")
        
    cid = df_c.iloc[0]["company_id"]
    df_docs = pd.read_sql("SELECT * FROM documents WHERE company_id = ?", conn, params=[cid])
    conn.close()
    
    records = df_docs.to_dict(orient="records")
    for r in records:
        r["is_url_valid"] = True if r.get("url") and str(r.get("url")).startswith("http") else False
    return records
