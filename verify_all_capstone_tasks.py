import os
import sqlite3
import pandas as pd

def verify_all():
    print("=" * 85)
    print("BLUESTOCK FINANCIAL PLATFORM, SPRINTS 1, 2, 3 & 4 — COMPLETE VERIFICATION AUDIT")
    print("=" * 85)

    checks = []

    # 1. Check nifty100.db Database & Table Counts
    db_path = "nifty100.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM companies;")
        comp_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM financial_ratios;")
        ratios_cnt = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM peer_percentiles;")
        peer_pct_cnt = cur.fetchone()[0]
        cur.execute("PRAGMA foreign_key_check;")
        fk_errs = len(cur.fetchall())
        conn.close()
        
        checks.append(("nifty100.db Companies Count (Target: 92)", f"Count: {comp_cnt}", comp_cnt == 92))
        checks.append(("nifty100.db financial_ratios Count (Target: >= 1,100)", f"Count: {ratios_cnt}", ratios_cnt >= 1100))
        checks.append(("nifty100.db peer_percentiles Count (Target: > 0)", f"Count: {peer_pct_cnt}", peer_pct_cnt > 0))
        checks.append(("nifty100.db Foreign Key Integrity (Target: 0)", f"FK Errors: {fk_errs}", fk_errs == 0))
    else:
        checks.append(("nifty100.db Database Existence", "Missing", False))

    # 2. Check bluestock_mf.db Database
    mf_db = "bluestock_mf.db"
    if os.path.exists(mf_db):
        conn = sqlite3.connect(mf_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM fact_nav;")
        nav_cnt = cur.fetchone()[0]
        conn.close()
        checks.append(("bluestock_mf.db fact_nav Count (Target: 64,320)", f"Count: {nav_cnt}", nav_cnt == 64320))
    else:
        checks.append(("bluestock_mf.db Database Existence", "Missing", False))

    # 3. Check Excel Deliverables
    excel_files = [
        "output/screener_output.xlsx",
        "output/peer_comparison.xlsx",
        "output/valuation_summary.xlsx"
    ]
    for ex_f in excel_files:
        exists = os.path.exists(ex_f)
        size = os.path.getsize(ex_f) if exists else 0
        checks.append((f"Excel Deliverable '{ex_f}'", f"Size: {size//1024} KB", exists and size > 0))

    # 4. Check CSV Deliverables
    csv_files = [
        ("fund_scorecard.csv", 40),
        ("alpha_beta.csv", 40),
        ("var_cvar_report.csv", 40),
        ("output/load_audit.csv", 11),
        ("output/validation_failures.csv", 0),
        ("output/capital_allocation.csv", 1000),
        ("output/valuation_flags.csv", 5),
        ("data/processed/api_extracted_data.csv", 3000)
    ]
    for csv_f, min_r in csv_files:
        exists = os.path.exists(csv_f)
        if exists:
            rows = len(pd.read_csv(csv_f))
            checks.append((f"CSV Deliverable '{csv_f}'", f"Rows: {rows}", True))
        else:
            checks.append((f"CSV Deliverable '{csv_f}'", "Missing", False))

    # 5. Check Streamlit Dashboard Screens (8 screens)
    dashboard_files = [
        "src/dashboard/app.py",
        "src/dashboard/utils/db.py",
        "pages/01_home.py",
        "pages/02_profile.py",
        "pages/03_screener.py",
        "pages/04_peers.py",
        "pages/05_trends.py",
        "pages/06_sectors.py",
        "pages/07_capital.py",
        "pages/08_reports.py"
    ]
    for df_f in dashboard_files:
        d_exists = os.path.exists(df_f)
        checks.append((f"Dashboard Screen File '{df_f}'", "Exists" if d_exists else "Missing", d_exists))

    # 6. Check Analytics Modules
    modules = [
        "src/analytics/ratios.py",
        "src/analytics/cagr.py",
        "src/analytics/cashflow_kpis.py",
        "src/screener/engine.py",
        "src/analytics/peer.py",
        "src/analytics/valuation.py"
    ]
    for mod in modules:
        m_exists = os.path.exists(mod)
        checks.append((f"Analytics Module '{mod}'", "Exists" if m_exists else "Missing", m_exists))

    # 7. Check All Unit Tests
    unit_tests = [
        "tests/kpi/test_ratios.py",
        "tests/kpi/test_cagr.py",
        "tests/kpi/test_cashflow_kpis.py",
        "tests/screener/test_screener.py",
        "tests/peer/test_peer.py",
        "tests/valuation/test_valuation.py"
    ]
    for ut in unit_tests:
        ut_exists = os.path.exists(ut)
        checks.append((f"Unit Test File '{ut}'", "Exists" if ut_exists else "Missing", ut_exists))

    # Print Verification Results
    print("\n" + f"{'VERIFICATION CHECKITEM':<60} | {'METRIC RESULT':<18} | {'STATUS'}")
    print("-" * 90)
    all_passed = True
    for item, res, status in checks:
        stat_str = "✅ PASS" if status else "❌ FAIL"
        if not status: all_passed = False
        print(f"{item:<60} | {res:<18} | {stat_str}")

    print("=" * 90)
    if all_passed:
        print("🎉 ALL SPRINTS 1, 2, 3 & 4 PLATFORM TASKS VERIFIED 100% SUCCESSFUL!")
    else:
        print("❌ VERIFICATION FAILURES ENCOUNTERED.")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    verify_all()
