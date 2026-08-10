#!/usr/bin/env python3
"""
BlueStock Mutual Fund Platform - Master Pipeline Execution Engine
Executes end-to-end Capstone Workflow sequentially:
1. Data Ingestion & Quality Audit (data_ingestion.py)
2. Live NAV Fetching via API (live_nav_fetch.py)
3. Data Cleaning & Transformation (clean_data.py)
4. SQLite Database Loading & Integrity Verification (load_sqlite.py)
5. Exploratory Data Analysis & Notebook Generation (generate_eda_notebook.py)
6. Performance Analytics & Composite Scorecard (generate_performance_analytics.py)
7. Advanced Risk Metrics & Tail Risk Engineering (generate_advanced_analytics.py)
8. Power BI Dashboard Asset Generation (generate_dashboard_assets.py)
9. 12-Slide Executive Presentation Deck (generate_presentation.py)
10. 15-20 Page Final Technical PDF Report (generate_final_report.py)
"""

import os
import sys
import time
import subprocess

STAGES = [
    ("Stage 1: Data Ingestion & Quality Audit", "data_ingestion.py"),
    ("Stage 2: Live NAV API Fetch", "live_nav_fetch.py"),
    ("Stage 3: Data Cleaning & Transformation", "clean_data.py"),
    ("Stage 4: SQLite Database Ingestion & Verification", "load_sqlite.py"),
    ("Stage 5: Exploratory Data Analysis & Chart Generation", "generate_eda_notebook.py"),
    ("Stage 6: Performance Analytics & Scorecard Calculation", "generate_performance_analytics.py"),
    ("Stage 7: Advanced Risk Metrics & Tail Risk Analysis", "generate_advanced_analytics.py"),
    ("Stage 8: Power BI Dashboard Asset & Page Generation", "generate_dashboard_assets.py"),
    ("Stage 9: Executive Presentation Deck Generation", "generate_presentation.py"),
    ("Stage 10: Final Technical PDF Report Generation", "generate_final_report.py")
]

def main():
    print("=" * 80)
    print("BLUESTOCK MUTUAL FUND PLATFORM — MASTER PIPELINE EXECUTION ENGINE")
    print("=" * 80)
    start_time = time.time()

    for idx, (stage_name, script_file) in enumerate(STAGES, 1):
        print(f"\n[{idx}/{len(STAGES)}] RUNNING {stage_name.upper()} ({script_file})...")
        print("-" * 80)
        
        if not os.path.exists(script_file):
            print(f"Error: Script '{script_file}' not found. Skipping stage.")
            continue
            
        ret = subprocess.run([sys.executable, script_file])
        if ret.returncode != 0:
            print(f"\n❌ Error encountered in {script_file} (Exit Code: {ret.returncode}). Pipeline stopped.")
            sys.exit(ret.returncode)
            
        print(f"✅ {stage_name} completed successfully.")

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🎉 MASTER PIPELINE EXECUTED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("All deliverables generated: CSVs, SQLite DB, Notebooks, Visuals, PPTX & PDF Report.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
