#!/usr/bin/env python3
"""
Shared Streamlit Data Loader (src/dashboard/utils/db.py)
Provides cached database query functions using @st.cache_data(ttl=600).
Functions:
  - get_companies()
  - get_ratios(ticker, year=None)
  - get_pl(ticker)
  - get_bs(ticker)
  - get_cf(ticker)
  - get_sectors()
  - get_peers(group_name)
  - get_valuation(ticker)
  - get_documents(ticker)
  - get_prosandcons(ticker)
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
from typing import Optional, List, Dict

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")

def get_db_connection():
    target_db = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    return sqlite3.connect(target_db)


@st.cache_data(ttl=600)
def get_companies() -> pd.DataFrame:
    """Returns all 92 companies with metadata."""
    conn = get_db_connection()
    df = pd.read_sql("SELECT * FROM companies ORDER BY company_name ASC", conn)
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_ratios(ticker: Optional[str] = None, year: Optional[int] = None) -> pd.DataFrame:
    """Returns financial ratios merged with company metadata."""
    conn = get_db_connection()
    query = """
    SELECT c.company_id, c.ticker, c.company_name, c.sector, c.industry, r.*
    FROM financial_ratios r
    JOIN companies c ON r.company_id = c.company_id
    WHERE 1=1
    """
    params = []
    if ticker:
        query += " AND (c.ticker = ? OR c.company_name LIKE ?)"
        params.extend([ticker.upper(), f"%{ticker}%"])
    if year:
        query += " AND r.year = ?"
        params.append(year)
        
    query += " ORDER BY c.ticker ASC, r.year ASC"
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_pl(ticker: str) -> pd.DataFrame:
    """Returns 10-year Profit & Loss statement for a company."""
    conn = get_db_connection()
    query = """
    SELECT p.* FROM profitandloss p
    JOIN companies c ON p.company_id = c.company_id
    WHERE c.ticker = ? OR c.company_name LIKE ?
    ORDER BY p.year ASC
    """
    df = pd.read_sql(query, conn, params=[ticker.upper(), f"%{ticker}%"])
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_bs(ticker: str) -> pd.DataFrame:
    """Returns Balance Sheet data for a company."""
    conn = get_db_connection()
    query = """
    SELECT b.* FROM balancesheet b
    JOIN companies c ON b.company_id = c.company_id
    WHERE c.ticker = ? OR c.company_name LIKE ?
    ORDER BY b.year ASC
    """
    df = pd.read_sql(query, conn, params=[ticker.upper(), f"%{ticker}%"])
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_cf(ticker: str) -> pd.DataFrame:
    """Returns Cash Flow data for a company."""
    conn = get_db_connection()
    query = """
    SELECT cf.* FROM cashflow cf
    JOIN companies c ON cf.company_id = c.company_id
    WHERE c.ticker = ? OR c.company_name LIKE ?
    ORDER BY cf.year ASC
    """
    df = pd.read_sql(query, conn, params=[ticker.upper(), f"%{ticker}%"])
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_sectors() -> pd.DataFrame:
    """Returns sector list with company counts."""
    conn = get_db_connection()
    query = """
    SELECT sector, COUNT(company_id) AS company_count
    FROM companies
    GROUP BY sector
    ORDER BY company_count DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_peers(group_name: Optional[str] = None) -> pd.DataFrame:
    """Returns peer percentiles data."""
    conn = get_db_connection()
    query = """
    SELECT p.*, c.ticker, c.company_name, c.sector
    FROM peer_percentiles p
    JOIN companies c ON p.company_id = c.company_id
    WHERE 1=1
    """
    params = []
    if group_name:
        query += " AND p.peer_group_name = ?"
        params.append(group_name)
        
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_documents(ticker: str) -> pd.DataFrame:
    """Returns annual report documents for a company."""
    conn = get_db_connection()
    query = """
    SELECT d.* FROM documents d
    JOIN companies c ON d.company_id = c.company_id
    WHERE c.ticker = ? OR c.company_name LIKE ?
    """
    df = pd.read_sql(query, conn, params=[ticker.upper(), f"%{ticker}%"])
    conn.close()
    return df


@st.cache_data(ttl=600)
def get_prosandcons(ticker: str) -> pd.DataFrame:
    """Returns Pros and Cons qualitative records for a company."""
    conn = get_db_connection()
    query = """
    SELECT pc.* FROM prosandcons pc
    JOIN companies c ON pc.company_id = c.company_id
    WHERE c.ticker = ? OR c.company_name LIKE ?
    """
    df = pd.read_sql(query, conn, params=[ticker.upper(), f"%{ticker}%"])
    conn.close()
    return df
