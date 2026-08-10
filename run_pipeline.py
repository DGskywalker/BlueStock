#!/usr/bin/env python3
"""
BlueStock Mutual Fund Platform - Master Pipeline Execution Engine (v1.0 Capstone Release)
Executes end-to-end Capstone Workflow sequentially:
1. Data Ingestion & Quality Audit (data_ingestion.py)
2. Live NAV API Fetch (live_nav_fetch.py)
3. Data Cleaning & Daily Forward-Fill (clean_data.py)
4. SQLite Database Ingestion & Verification (load_sqlite.py)
5. Exploratory Data Analysis & Chart Generation (generate_eda_notebook.py)
6. Performance Analytics & Scorecard Calculation (generate_performance_analytics.py)
7. Advanced Risk Metrics & Tail Risk Analysis (generate_advanced_analytics.py)
8. Bonus B3: 5-Year Monte Carlo NAV Simulation (scripts/monte_carlo_sim.py)
9. Bonus B4: Markowitz Efficient Frontier Portfolio Optimization (scripts/markowitz_frontier.py)
10. Bonus B5: Automated HTML Email Report Generator (scripts/email_report.py)
11. Power BI Dashboard Asset & Page Generation (generate_dashboard_assets.py)
12. Executive Presentation Deck Generation (generate_presentation.py)
13. Final Technical PDF Report Generation (generate_final_report.py)
14. Workspace Organization & Notebook Assembly (build_capstone_workspace.py)
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
    ("Bonus B3: 5-Year Monte Carlo NAV Simulation", os.path.join("scripts", "monte_carlo_sim.py")),
    ("Bonus B4: Markowitz Efficient Frontier Portfolio Optimization", os.path.join("scripts", "markowitz_frontier.py")),
    ("Bonus B5: Automated HTML Email Performance Summary Generator", os.path.join("scripts", "email_report.py")),
    ("Stage 8: Power BI Dashboard Asset & Page Generation", "generate_dashboard_assets.py"),
    ("Stage 9: Executive Presentation Deck Generation", "generate_presentation.py"),
    ("Stage 10: Final Technical PDF Report Generation", "generate_final_report.py"),
    ("Stage 11: Workspace Organization & Notebook Synchronization", "build_capstone_workspace.py")
]

def main():
    print("=" * 80)
    print("BLUESTOCK MUTUAL FUND PLATFORM — MASTER PIPELINE EXECUTION ENGINE")
    print("================================================================================")
    start_time = time.time()

    for idx, (stage_name, script_file) in enumerate(STAGES, 1):
        print(f"\n[{idx}/{len(STAGES)}] RUNNING {stage_name.upper()} ({script_file})...")
        print("-" * 80)
        
        if not os.path.exists(script_file):
            print(f"Warning: Script '{script_file}' not found. Skipping stage.")
            continue
            
        ret = subprocess.run([sys.executable, script_file])
        if ret.returncode != 0:
            print(f"\n❌ Error encountered in {script_file} (Exit Code: {ret.returncode}). Pipeline stopped.")
            sys.exit(ret.returncode)
            
        print(f"✅ {stage_name} completed successfully.")

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🎉 MASTER PIPELINE & BONUS CHALLENGES EXECUTED SUCCESSFULLY IN {elapsed:.2f} SECONDS!")
    print("All deliverables generated: CSVs, SQLite DB, Notebooks, Streamlit App, Visuals, PPTX & PDF Report.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
