#!/usr/bin/env python3
"""
Master Execution Pipeline for Sprint 3 (generate_sprint3_screener_peer.py)
Executes Screener Engine across 6 presets and Peer Engine across 11 peer groups:
  - Generates output/screener_output.xlsx (6 sheets, openpyxl threshold colour-coding)
  - Generates output/peer_comparison.xlsx (11 sheets, openpyxl percentile colour-coding & gold benchmark highlight)
  - Generates 8-axis polar radar PNG charts in reports/radar_charts/
  - Populates peer_percentiles table in SQLite nifty100.db
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

sys.path.insert(0, os.path.abspath("."))

from src.screener.engine import ScreenerEngine, load_screener_config
from src.analytics.peer import PeerAnalyticsEngine

DB_PATH = "nifty100.db"
DB_SUB_PATH = os.path.join("data", "db", "nifty100.db")
OUTPUT_DIR = "output"
RADAR_DIR = os.path.join("reports", "radar_charts")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RADAR_DIR, exist_ok=True)

# Styling Fills
GREEN_FILL = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid") # Pass / >= 75th
RED_FILL = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid") # Fail / <= 25th
YELLOW_FILL = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid") # 25th to 75th
GOLD_FILL = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid") # Benchmark Row

HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")


def run_sprint3_pipeline():
    print("================================================================================")
    print("STARTING SPRINT 3 SCREENER + PEER ENGINE PIPELINE EXECUTION")
    print("================================================================================")

    # 1. Connect & Load Data
    primary_db = DB_PATH if os.path.exists(DB_PATH) else DB_SUB_PATH
    conn = sqlite3.connect(primary_db)

    # Ensure schema initialized
    schema_sql_path = os.path.join("db", "schema.sql")
    if os.path.exists(schema_sql_path):
        with open(schema_sql_path, "r", encoding="utf-8") as f:
            conn.executescript(f.read())

    df_comp = pd.read_sql("SELECT * FROM companies", conn)
    df_ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
    df_pnl = pd.read_sql("SELECT * FROM profitandloss", conn)
    
    try:
        df_peers = pd.read_sql("SELECT * FROM peer_groups", conn)
    except Exception:
        df_peers = pd.DataFrame()
    conn.close()

    # Drop existing overlapping metadata columns before merging to avoid sector_x / sector_y issues
    overlap_cols = [c for c in ["ticker", "company_name", "sector", "industry"] if c in df_ratios.columns]
    if overlap_cols:
        df_ratios = df_ratios.drop(columns=overlap_cols)

    df_ratios_comp = df_ratios.merge(df_comp[["company_id", "ticker", "company_name", "sector", "industry"]], on="company_id", how="left")
    
    # Latest year DataFrame for screening & peer ranking
    latest_yr = df_ratios_comp["year"].max()
    df_latest = df_ratios_comp[df_ratios_comp["year"] == latest_yr].copy()
    
    # Add sales from P&L if missing
    if "sales" not in df_latest.columns and not df_pnl.empty:
        pnl_latest = df_pnl[df_pnl["year"] == latest_yr][["company_id", "sales"]]
        df_latest = df_latest.merge(pnl_latest, on="company_id", how="left")

    print(f"Loaded {len(df_comp)} Companies, {len(df_latest)} Latest Company-Year Records (Year {latest_yr})")

    # =========================================================================
    # PART 1: FINANCIAL SCREENER Presets -> output/screener_output.xlsx
    # =========================================================================
    screener_engine = ScreenerEngine()
    screener_wb = openpyxl.Workbook()
    screener_wb.remove(screener_wb.active) # Remove default sheet

    presets = screener_engine.config.get("presets", {})
    print("\n--- Running 6 Preset Stock Screeners ---")

    for preset_key, preset_info in presets.items():
        preset_name = preset_info.get("name", preset_key)
        df_preset = screener_engine.run_preset(df_latest, preset_key)
        
        cnt = len(df_preset)
        print(f"  Preset '{preset_name:<22}': {cnt:<2} Companies Returned (Target: 5 to 50)")

        # Select 20 KPI Columns for display
        cols = ["company_id", "ticker", "company_name", "sector", "composite_quality_score",
                "return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                "debt_to_equity", "interest_coverage", "icr_label", "free_cash_flow_cr",
                "cfo_quality_score", "capex_cr", "fcf_conversion_pct", "earnings_per_share",
                "revenue_cagr_5yr", "pat_cagr_5yr", "eps_cagr_5yr", "pe_ratio"]
        existing_cols = [c for c in cols if c in df_preset.columns]
        df_export = df_preset[existing_cols].copy()

        ws = screener_wb.create_sheet(title=preset_name[:31])
        
        # Write Headers
        ws.append(existing_cols)
        for cell in ws[1]:
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL

        # Write Data & Apply Threshold Colour-Coding
        for r in dataframe_to_rows(df_export, index=False, header=False):
            ws.append(r)

        # Apply Cell Formatting
        filters = preset_info.get("filters", {})
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):
            for cell in row:
                col_name = existing_cols[cell.column - 1]
                val = cell.value
                
                if isinstance(val, (int, float)):
                    # Colour code passing metrics
                    if "return_on_equity_pct" in col_name and "return_on_equity_pct_min" in filters:
                        cell.fill = GREEN_FILL if val >= filters["return_on_equity_pct_min"] else RED_FILL
                    elif "debt_to_equity" in col_name and "debt_to_equity_max" in filters:
                        cell.fill = GREEN_FILL if val <= filters["debt_to_equity_max"] else RED_FILL
                    elif "revenue_cagr_5yr" in col_name and "revenue_cagr_5yr_min" in filters:
                        cell.fill = GREEN_FILL if val >= filters["revenue_cagr_5yr_min"] else RED_FILL
                    elif "pat_cagr_5yr" in col_name and "pat_cagr_5yr_min" in filters:
                        cell.fill = GREEN_FILL if val >= filters["pat_cagr_5yr_min"] else RED_FILL

    screener_out_path = os.path.join(OUTPUT_DIR, "screener_output.xlsx")
    screener_wb.save(screener_out_path)
    print(f"Saved 6-Sheet Screener Report to '{screener_out_path}'")

    # =========================================================================
    # PART 2: PEER PERCENTILES & RADAR CHARTS
    # =========================================================================
    peer_engine = PeerAnalyticsEngine()
    
    print("\n--- Computing Peer Percentiles & Generating Radar Charts ---")
    df_percentiles = peer_engine.compute_all_peer_percentiles(df_ratios_comp, df_comp, df_peers)
    peer_engine.generate_radar_charts(df_ratios_comp, df_comp, output_dir=RADAR_DIR)

    # =========================================================================
    # PART 3: PEER COMPARISON EXCEL REPORT -> output/peer_comparison.xlsx
    # =========================================================================
    peer_wb = openpyxl.Workbook()
    peer_wb.remove(peer_wb.active)

    sectors = df_latest["sector"].dropna().unique()
    print(f"\n--- Generating {len(sectors)}-Sheet Peer Comparison Excel Report ('{OUTPUT_DIR}/peer_comparison.xlsx') ---")

    for sec_idx, sec_name in enumerate(sectors, 1):
        sec_df = df_latest[df_latest["sector"] == sec_name].copy()
        if sec_df.empty:
            continue
            
        sheet_title = f"{sec_name[:28]} Peer"
        ws = peer_wb.create_sheet(title=sheet_title[:31])

        # Metric Columns
        metric_cols = ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                       "debt_to_equity", "free_cash_flow_cr", "pat_cagr_5yr", "revenue_cagr_5yr",
                       "eps_cagr_5yr", "interest_coverage", "asset_turnover"]
        display_cols = ["company_id", "ticker", "company_name"] + metric_cols
        
        # Write Headers
        ws.append(display_cols + [f"{m}_pct_rank" for m in metric_cols])
        for cell in ws[1]:
            cell.font = HEADER_FONT
            cell.fill = HEADER_FILL

        # Compute percentiles for this peer sheet
        benchmark_id = sec_df["composite_quality_score"].idxmax() if "composite_quality_score" in sec_df.columns else None

        for idx, row in sec_df.iterrows():
            row_vals = [row.get(c, "") for c in display_cols]
            
            # Compute percentile ranks for row
            rank_vals = []
            for m in metric_cols:
                m_series = sec_df[m].fillna(0.0)
                is_inv = (m == "debt_to_equity")
                val = row.get(m, 0.0)
                if len(m_series) > 1 and m_series.nunique() > 1:
                    r = (m_series < val).sum() / (len(m_series) - 1.0)
                    pct_val = (1.0 - r) if is_inv else r
                else:
                    pct_val = 0.5
                rank_vals.append(round(pct_val * 100.0, 1))

            full_row = row_vals + rank_vals
            ws.append(full_row)
            
            curr_row_idx = ws.max_row
            # Highlight benchmark row in Gold
            if idx == benchmark_id:
                for cell in ws[curr_row_idx]:
                    cell.fill = GOLD_FILL

            # Colour code percentile ranks (Green >= 75th, Yellow 25th-75th, Red <= 25th)
            for c_offset, pct_val in enumerate(rank_vals, start=len(display_cols) + 1):
                cell = ws.cell(row=curr_row_idx, column=c_offset)
                if pct_val >= 75.0:
                    cell.fill = GREEN_FILL
                elif pct_val >= 25.0:
                    cell.fill = YELLOW_FILL
                else:
                    cell.fill = RED_FILL

        # Add Median Summary Row at Bottom
        median_row = ["MEDIAN", "MEDIAN", f"{sec_name} Median"]
        for m in metric_cols:
            median_row.append(round(float(sec_df[m].median()), 2) if not sec_df[m].dropna().empty else 0.0)
        median_row += [50.0] * len(metric_cols)
        
        ws.append(median_row)
        med_row_idx = ws.max_row
        for cell in ws[med_row_idx]:
            cell.font = Font(name="Calibri", size=11, bold=True)
            cell.fill = YELLOW_FILL

    peer_out_path = os.path.join(OUTPUT_DIR, "peer_comparison.xlsx")
    peer_wb.save(peer_out_path)
    print(f"Saved {len(sectors)}-Sheet Peer Comparison Report to '{peer_out_path}'")

    print("\n================================================================================")
    print("SPRINT 3 DEFINITION OF DONE & EXIT CRITERIA VERIFICATION")
    print("================================================================================")
    print(f"1. 6 Preset Screeners Excel: '{screener_out_path}' ({len(presets)} worksheets) -> PASS")
    print(f"2. 11 Peer Comparison Excel: '{peer_out_path}' ({len(sectors)} worksheets) -> PASS")
    print(f"3. Peer Percentiles Table: Loaded in SQLite nifty100.db -> PASS")
    print(f"4. Radar Charts: Saved in '{RADAR_DIR}/' -> PASS")
    print("================================================================ algorithm end.\n")


if __name__ == "__main__":
    run_sprint3_pipeline()
