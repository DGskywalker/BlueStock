#!/usr/bin/env python3
"""
Valuation Engine (src/analytics/valuation.py)
Computes FCF Yield, 5-year Median P/E, Sector Median P/E Comparisons, and Overvaluation Flags (Caution, Discount, Fair).
Exports:
  - output/valuation_summary.xlsx (92 companies)
  - output/valuation_flags.csv (Caution & Discount flagged companies)
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def compute_valuation_metrics(df_ratios: pd.DataFrame, df_companies: pd.DataFrame,
                               df_pnl: pd.DataFrame) -> pd.DataFrame:
    """
    Computes FCF Yield, Sector Median P/E, and Overvaluation Flags (Caution / Discount / Fair).
    """
    df_merged = df_ratios.merge(df_companies[["company_id", "ticker", "company_name", "sector"]], on="company_id", how="left")
    latest_yr = df_merged["year"].max()
    df_latest = df_merged[df_merged["year"] == latest_yr].copy()

    # Calculate Market Cap proxy (Sales * 2.5 if market cap not in DB)
    if "sales" not in df_latest.columns and not df_pnl.empty:
        pnl_latest = df_pnl[df_pnl["year"] == latest_yr][["company_id", "sales"]]
        df_latest = df_latest.merge(pnl_latest, on="company_id", how="left")
        
    df_latest["market_cap_crore"] = df_latest["sales"].fillna(5000.0) * 2.5

    # Compute FCF Yield (%)
    df_latest["fcf_yield_pct"] = np.where(
        df_latest["market_cap_crore"] > 0,
        (df_latest["free_cash_flow_cr"].fillna(0.0) / df_latest["market_cap_crore"]) * 100.0,
        0.0
    ).round(2)

    # EV / EBITDA proxy
    df_latest["ev_to_ebitda"] = (df_latest["pe_ratio"].fillna(20.0) * 0.75).round(2)

    # 5-Year Median P/E per company
    pe_5yr_med = df_merged.groupby("company_id")["pe_ratio"].median().to_dict()
    df_latest["median_5yr_pe"] = df_latest["company_id"].map(pe_5yr_med).round(2)

    # Sector Median P/E
    sec_pe_med = df_latest.groupby("sector")["pe_ratio"].median().to_dict()
    df_latest["sector_median_pe"] = df_latest["sector"].map(sec_pe_med).fillna(20.0)

    # P/E vs Sector Median % Difference
    df_latest["pe_vs_sector_median_pct"] = np.where(
        df_latest["sector_median_pe"] > 0,
        ((df_latest["pe_ratio"].fillna(20.0) - df_latest["sector_median_pe"]) / df_latest["sector_median_pe"]) * 100.0,
        0.0
    ).round(2)

    # Overvaluation Flag Classification
    # Caution: P/E > sector_median * 1.5 | Discount: P/E < sector_median * 0.7 | Fair: otherwise
    conditions = [
        df_latest["pe_ratio"] > (df_latest["sector_median_pe"] * 1.5),
        df_latest["pe_ratio"] < (df_latest["sector_median_pe"] * 0.7)
    ]
    choices = ["Caution", "Discount"]
    df_latest["valuation_flag"] = np.select(conditions, choices, default="Fair")

    # Select & Order Required Valuation Columns
    cols = ["company_id", "ticker", "company_name", "sector", "pe_ratio", "pb_ratio",
            "ev_to_ebitda", "fcf_yield_pct", "median_5yr_pe", "sector_median_pe",
            "pe_vs_sector_median_pct", "valuation_flag"]
            
    df_valuation = df_latest[cols].copy().sort_values("pe_vs_sector_median_pct", ascending=False)
    return df_valuation


def export_valuation_reports(df_valuation: pd.DataFrame, output_dir: str = "output/"):
    """Exports output/valuation_summary.xlsx and output/valuation_flags.csv."""
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Valuation Summary Excel
    excel_path = os.path.join(output_dir, "valuation_summary.xlsx")
    df_valuation.to_excel(excel_path, index=False)
    
    # 2. Valuation Flags CSV (Caution & Discount companies only)
    flags_csv_path = os.path.join(output_dir, "valuation_flags.csv")
    df_flags = df_valuation[df_valuation["valuation_flag"].isin(["Caution", "Discount"])].copy()
    df_flags.to_csv(flags_csv_path, index=False)
    
    print(f"Saved Valuation Summary Excel ({len(df_valuation)} rows) to '{excel_path}'")
    print(f"Saved Valuation Flags CSV ({len(df_flags)} rows) to '{flags_csv_path}'")
    return excel_path, flags_csv_path
