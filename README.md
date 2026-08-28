# 📊 BlueStock Mutual Fund Analytics & Equity Research Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-yellow.svg)](https://powerbi.microsoft.com/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red.svg)](https://streamlit.io/)
[![Unit Tests](https://img.shields.io/badge/Tests-66%20Passed-brightgreen.svg)](https://github.com/DGskywalker/BlueStock)
[![Release](https://img.shields.io/badge/Release-v1.0-brightgreen.svg)](https://github.com/DGskywalker/BlueStock/releases/tag/v1.0)

An end-to-end data engineering, equity research, financial ratio engine, quantitative risk analytics, and interactive visualization platform built for **Bluestock Fintech**. 

The platform automates raw data ingestion, 16 Data Quality validation rules, SQLite database loading (`nifty100.db` & `bluestock_mf.db`), 50+ financial ratio calculations, multi-year CAGR edge-case handling, an 8-pattern capital allocation classifier, 6 preset stock screeners, 11 peer group percentile rankings, 92 polar radar PNG visualizations, quantitative portfolio risk diagnostics (VaR, CVaR, Sharpe, Beta), a Streamlit web application, a 4-page Power BI dashboard, and executive PDF reporting engines.

---

## 📌 Project Architecture & Sprint Roadmap

```
BlueStock Platform Architecture
├── 1. Data Foundation (Sprint 1) ---------> SQLite nifty100.db (10 Tables, 16 DQ Rules, 35 Tests)
├── 2. Financial Ratio Engine (Sprint 2) ---> 50+ KPIs, 8-Pattern Capital Allocation, 23 KPI Tests
├── 3. Screener & Peer Engine (Sprint 3) ---> 6 Presets, P10/P90 Winsorised Composite Score, 11 Peer Groups, 92 Radar PNGs
├── 4. Mutual Fund Capstone --------------> 40 Schemes, VaR (95%), CVaR, Sharpe, Beta, Recommender
├── 5. Web & Executive Dashboards ---------> Streamlit Web App (app.py) & Power BI (4 Pages, index.html)
└── 6. Verification & Build System ---------> Makefile (make test / make screener) & verify_all_capstone_tasks.py
```

---

## 🏆 Key Sprint Deliverables & Manifest

### Sprint 1: Data Foundation (34 Story Points)
- **SQLite Database (`nifty100.db`)**: 10 relational tables (`companies`, `profitandloss`, `balancesheet`, `cashflow`, `financial_ratios`, `analysis`, `documents`, `prosandcons`, `sectors`, `stock_prices`, `peer_groups`).
- **Data Quality Validator (`src/etl/validator.py`)**: 16 DQ rules (DQ-01 to DQ-16) covering primary key uniqueness, foreign key integrity, balance sheet balance, OPM cross-checks, tax rate bounds, URL validation, and price outlier detection.
- **ETL Loader & Normaliser (`src/etl/loader.py` & `src/etl/normaliser.py`)**: Automatic financial year normalisation (`normalize_year`) and ticker cleaning (`normalize_ticker`).
- **Audit Reports**: [`output/load_audit.csv`](file:///Users/divyanshgupta/Desktop/BlueStock/output/load_audit.csv) and [`output/validation_failures.csv`](file:///Users/divyanshgupta/Desktop/BlueStock/output/validation_failures.csv).
- **Analytical SQL Queries**: [`notebooks/exploratory_queries.sql`](file:///Users/divyanshgupta/Desktop/BlueStock/notebooks/exploratory_queries.sql) (10 production analytical SQL queries).

### Sprint 2: Financial Ratio Engine (42 Story Points)
- **Profitability, Leverage & Efficiency Module (`src/analytics/ratios.py`)**: NPM, OPM cross-check, ROE negative equity check, ROCE bank carve-out, ROA, D/E debt-free `0.0` handling, High Leverage flag (suppressed for Financials), ICR `"Debt Free"` label & warning flag, Net Debt, Asset Turnover.
- **CAGR Engine (`src/analytics/cagr.py`)**: 3Y, 5Y, and 10Y Revenue, PAT, and EPS CAGR calculations with 6 edge-case flag handlers (`NORMAL`, `DECLINE_TO_LOSS`, `TURNAROUND`, `BOTH_NEGATIVE`, `ZERO_BASE`, `INSUFFICIENT`).
- **Cash Flow KPIs & Capital Allocation (`src/analytics/cashflow_kpis.py`)**: Free Cash Flow (FCF), 5Y CFO Quality Score, CapEx Intensity, FCF Conversion, and 8-pattern Capital Allocation Classifier (`Reinvestor`, `Shareholder Returns`, `Liquidating Assets`, `Distress Signal`, `Growth Funded by Debt`, `Cash Accumulator`, `Pre-Revenue`, `Mixed`).
- **Database Table (`financial_ratios`)**: 1,312 rows loaded into `nifty100.db` with 42 KPI columns populated.
- **Reports**: [`output/capital_allocation.csv`](file:///Users/divyanshgupta/Desktop/BlueStock/output/capital_allocation.csv) (1,187 rows) and [`output/ratio_edge_cases.log`](file:///Users/divyanshgupta/Desktop/BlueStock/output/ratio_edge_cases.log).

### Sprint 3: Screener & Peer Engine (49 Story Points)
- **Screener Configuration (`config/screener_config.yaml`)**: Analyst-editable threshold definitions for 6 preset stock screeners supporting 15 filterable metrics.
- **Screener Engine (`src/screener/engine.py`)**:
  - `Quality Compounder`: ROE > 16.5%, D/E < 0.35, FCF > 0, Revenue CAGR 5Y > 10%
  - `Value Pick`: P/E < 22, P/B < 3.5, D/E < 0.8, Dividend Yield > 1.0%
  - `Growth Accelerator`: PAT CAGR 5Y > 12%, Revenue CAGR 5Y > 10%, D/E < 0.8
  - `Dividend Champion`: Dividend Yield > 1.5%, Payout < 70%, FCF > 0
  - `Debt-Free Blue Chip`: D/E <= 0.35, ROE > 15%, Sales > ₹5,000 Cr
  - `Turnaround Watch`: Revenue CAGR 3Y > 10%, FCF > 0, D/E <= 0.35
  - **P10/P90 Winsorised Composite Quality Score (0–100)**: 35% Profitability + 30% Cash Quality + 20% Growth + 15% Leverage, with sector-relative scaling.
- **Peer Analytics Engine (`src/analytics/peer.py`)**: `PERCENT_RANK` computed across 10 metrics for 11 peer groups in SQLite `peer_percentiles` table (920 rows). Inverse ranking applied to D/E.
- **Radar Chart Generator (`reports/radar_charts/`)**: 92 polar radar PNG charts with filled company polygons and dashed peer group average overlays.
- **Excel Exporters**:
  - [`output/screener_output.xlsx`](file:///Users/divyanshgupta/Desktop/BlueStock/output/screener_output.xlsx): 6 worksheets with green/red cell fill threshold formatting.
  - [`output/peer_comparison.xlsx`](file:///Users/divyanshgupta/Desktop/BlueStock/output/peer_comparison.xlsx): 11 worksheets with percentile colour-coding ($\ge 75\text{th}$ green, $25\text{th}-75\text{th}$ yellow, $\le 25\text{th}$ red), gold-highlighted benchmark rows, and median summary rows.

### Bonus Challenges (+50 Marks)
1. **B1 — Weekday 8 PM Cron Scheduler**: [`scripts/cron_scheduler.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/cron_scheduler.py)
2. **B2 — Streamlit Web Application**: [`app.py`](file:///Users/divyanshgupta/Desktop/BlueStock/app.py) & [`scripts/streamlit_app.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/streamlit_app.py)
3. **B3 — 5-Year Monte Carlo NAV Simulation**: [`scripts/monte_carlo_sim.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/monte_carlo_sim.py)
4. **B4 — Markowitz Efficient Frontier Portfolio Optimization**: [`scripts/markowitz_frontier.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/markowitz_frontier.py)
5. **B5 — Automated HTML Email Generator**: [`scripts/email_report.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/email_report.py)

### Week 2 Prerequisites & FinTech Research
- **Stock Market Summary & HDFC Bank Financial Analysis**: [`reports/prerequisites/Stock_Market_Summary_and_Financial_Analysis.pdf`](file:///Users/divyanshgupta/Desktop/BlueStock/reports/prerequisites/Stock_Market_Summary_and_Financial_Analysis.pdf)
- **REST API & JSON Extractor**: [`scripts/api_json_extractor.py`](file:///Users/divyanshgupta/Desktop/BlueStock/scripts/api_json_extractor.py) & [`data/processed/api_extracted_data.csv`](file:///Users/divyanshgupta/Desktop/BlueStock/data/processed/api_extracted_data.csv) (3,289 records parsed).
- **Software Architecture Diagram**: [`reports/prerequisites/Software_Architecture_Diagram.md`](file:///Users/divyanshgupta/Desktop/BlueStock/reports/prerequisites/Software_Architecture_Diagram.md)
- **FinTech Research Report**: [`reports/prerequisites/FinTech_Research_Report.pdf`](file:///Users/divyanshgupta/Desktop/BlueStock/reports/prerequisites/FinTech_Research_Report.pdf)

---

## ⚡ Setup & Execution Instructions

### 1. Installation & Environment
```bash
git clone https://github.com/DGskywalker/BlueStock.git
cd BlueStock
pip install -r requirements.txt
```

### 2. Makefile Automation Commands
```bash
make load        # Runs ETL pipeline, 16 DQ rules, and populates nifty100.db
make ratios      # Executes Financial Ratio Engine (50+ KPIs) into financial_ratios table
make screener    # Runs 6 Stock Screener Presets, 11 Peer Groups, Excel exports & Radar PNGs
make test        # Executes full 66+ unit test suite across tests/etl, tests/kpi, tests/screener, tests/peer
make report      # Generates 18-page technical report & 12-slide presentation deck
make dashboard   # Renders HTML web dashboard & Power BI assets
```

### 3. Automated Verification Audit
Run the verification audit script to validate all exit criteria:
```bash
python3 verify_all_capstone_tasks.py
```

### 4. Interactive Streamlit Web App
Launch the web interface:
```bash
streamlit run app.py
```

---

## 🧪 Unit Test Suite Verification (66 Unit Tests)

```bash
=== Running All Unit Test Suites (70+ Unit Tests across ETL, KPI, Screener & Peer) ===
python3 -m unittest discover -s tests/etl -p "test_*.py"       # 35 Passed in 0.012s - OK
python3 -m unittest discover -s tests/kpi -p "test_*.py"       # 23 Passed in 0.002s - OK
python3 -m unittest discover -s tests/screener -p "test_*.py"  #  5 Passed in 0.426s - OK
python3 -m unittest discover -s tests/peer -p "test_*.py"      #  3 Passed in 0.031s - OK
```

---

## 🏷️ GitHub Versioning & Release Tag
- **Version**: `v1.0`
- **Git Repository**: [https://github.com/DGskywalker/BlueStock](https://github.com/DGskywalker/BlueStock)
- **Commit History**:
  - `edad8d6` - Sprint 3: Epics 03 & 04 Screener + Peer Engine complete - 6 preset screeners, 11 peer groups, radar charts, Excel reports
  - `3518558` - Sprint 2: Epic 02 Financial Ratio Engine complete - 58 unit tests, financial_ratios table populated, capital allocation, edge case logs
  - `005557b` - Verification Audit: 100% Week 2 Prerequisites & Capstone Tasks Verified Passing
  - `984fa5b` - Sprint 1: Data Foundation complete - nifty100.db, 16 DQ rules, 35+ unit tests
