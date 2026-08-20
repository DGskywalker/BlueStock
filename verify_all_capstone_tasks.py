import os
import sqlite3
import pandas as pd

def verify_all():
    print("=" * 85)
    print("BLUESTOCK MUTUAL FUND & PREREQUISITES CAPSTONE — COMPLETE VERIFICATION AUDIT")
    print("=" * 85)

    checks = []

    # 1. Check nifty100.db Database
    db_path = "nifty100.db"
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM companies;")
        comp_cnt = cur.fetchone()[0]
        cur.execute("PRAGMA foreign_key_check;")
        fk_errs = len(cur.fetchall())
        conn.close()
        status_db = comp_cnt == 92 and fk_errs == 0
        checks.append(("nifty100.db Companies Count (Target: 92)", f"Count: {comp_cnt}", status_db))
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

    # 3. Check CSV Deliverables
    csv_files = [
        "fund_scorecard.csv",
        "alpha_beta.csv",
        "var_cvar_report.csv",
        "output/load_audit.csv",
        "output/validation_failures.csv",
        "data/processed/api_extracted_data.csv"
    ]
    for csv_f in csv_files:
        exists = os.path.exists(csv_f)
        if exists:
            rows = len(pd.read_csv(csv_f))
            checks.append((f"CSV Deliverable '{csv_f}'", f"Rows: {rows}", True))
        else:
            checks.append((f"CSV Deliverable '{csv_f}'", "Missing", False))

    # 4. Check PDF Reports
    pdf_files = [
        "reports/Final_Report.pdf",
        "reports/prerequisites/Stock_Market_Summary_and_Financial_Analysis.pdf",
        "reports/prerequisites/FinTech_Research_Report.pdf"
    ]
    for pdf_f in pdf_files:
        exists = os.path.exists(pdf_f)
        size = os.path.getsize(pdf_f) if exists else 0
        checks.append((f"PDF Report '{pdf_f}'", f"Size: {size//1024} KB", exists and size > 0))

    # 5. Check PPTX Presentation
    pptx_path = "reports/Bluestock_MF_Presentation.pptx"
    exists_pptx = os.path.exists(pptx_path)
    size_pptx = os.path.getsize(pptx_path) if exists_pptx else 0
    checks.append((f"PPTX Deck '{pptx_path}'", f"Size: {size_pptx//1024} KB", exists_pptx and size_pptx > 0))

    # 6. Check App & Web Dashboard
    app_exists = os.path.exists("app.py")
    checks.append(("Streamlit Web App 'app.py'", "Exists" if app_exists else "Missing", app_exists))
    
    html_exists = os.path.exists("dashboard/index.html")
    checks.append(("Interactive Web App 'dashboard/index.html'", "Exists" if html_exists else "Missing", html_exists))

    # 7. Check 6 Numbered Notebooks
    notebooks = [
        "notebooks/01_data_ingestion.ipynb",
        "notebooks/02_data_cleaning.ipynb",
        "notebooks/03_eda_analysis.ipynb",
        "notebooks/04_performance_analytics.ipynb",
        "notebooks/05_advanced_analytics.ipynb",
        "notebooks/06_api_data_extraction.ipynb"
    ]
    for nb in notebooks:
        exists = os.path.exists(nb)
        checks.append((f"Notebook '{nb}'", "Exists" if exists else "Missing", exists))

    # 8. Check Prerequisites Markdown Reports
    prereq_docs = [
        "reports/prerequisites/Stock_Market_Summary_and_Financial_Analysis.md",
        "reports/prerequisites/Software_Architecture_Diagram.md",
        "reports/prerequisites/FinTech_Research_Report.md"
    ]
    for doc in prereq_docs:
        exists = os.path.exists(doc)
        checks.append((f"Prerequisite Doc '{doc}'", "Exists" if exists else "Missing", exists))

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
        print("🎉 ALL WEEK 2 PREREQUISITES & CAPSTONE TASKS VERIFIED 100% SUCCESSFUL!")
    else:
        print("❌ VERIFICATION FAILURES ENCOUNTERED.")
    print("=" * 90 + "\n")

if __name__ == "__main__":
    verify_all()
