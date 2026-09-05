# 📊 BlueStock Financial Analytics & Equity Research Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-yellow.svg)](https://powerbi.microsoft.com/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red.svg)](https://streamlit.io/)
[![Unit Tests](https://img.shields.io/badge/Tests-66%20Passed-brightgreen.svg)](https://github.com/DGskywalker/BlueStock)
[![Release](https://img.shields.io/badge/Release-v1.0-brightgreen.svg)](https://github.com/DGskywalker/BlueStock/releases/tag/v1.0)

An end-to-end data engineering, equity research, financial ratio calculation engine, quantitative risk analytics, and interactive web dashboard platform built for **Bluestock Fintech**.

The platform automates raw financial data ingestion, executes 16 data quality validation rules, loads a relational SQLite database (`nifty100.db` & `bluestock_mf.db`), calculates 50+ financial ratios, handles multi-year CAGR edge cases, classifies capital allocation patterns, powers 6 preset stock screeners, evaluates 11 peer group percentile rankings, renders 92 polar radar visualizations, models mutual fund risk (VaR, CVaR, Sharpe, Beta), and serves interactive web and PDF reporting dashboards.

---

## 📌 System Architecture

```
BlueStock Platform Architecture
├── 1. Data Foundation & ETL ---------> Relational SQLite Database (nifty100.db, 16 DQ Rules)
├── 2. Financial Ratio Engine ---------> 50+ KPIs, 8-Pattern Capital Allocation Classifier
├── 3. Stock Screener & Peer Engine ---> 6 Presets, Winsorised Composite Quality Score, 92 Radar PNGs
├── 4. Mutual Fund & Risk Analytics ---> 40 Equity Schemes, 95% VaR, CVaR, Sharpe Ratio, Portfolio Beta
├── 5. Interactive Dashboards ---------> Streamlit Web Application (app.py) & Power BI Executive Dashboard
└── 6. Build & Automation -------------> Makefile Build Targets & Automated Test Suite (66 Unit Tests)
```

---

## 🚀 Key Modules & Features

### 1. Data Foundation & Ingestion Engine
- **Relational SQLite Database (`nifty100.db`)**: 10 relational tables (`companies`, `profitandloss`, `balancesheet`, `cashflow`, `financial_ratios`, `analysis`, `documents`, `prosandcons`, `sectors`, `stock_prices`, `peer_groups`).
- **Data Quality Validator (`src/etl/validator.py`)**: 16 automated validation rules covering primary key uniqueness, foreign key integrity, balance sheet balancing, OPM cross-checks, tax rate bounds, URL formatting, and price outlier detection.
- **ETL Loader & Normaliser (`src/etl/loader.py` & `src/etl/normaliser.py`)**: Standardises financial year formats and ticker symbols across incoming source files.
- **Data Audits**: Automated logging to `output/load_audit.csv` and `output/validation_failures.csv`.

### 2. Financial Ratio & Analytics Engine
- **Profitability, Leverage & Efficiency (`src/analytics/ratios.py`)**: Computes NPM, OPM cross-checks, ROE (with negative equity handling), ROCE (with banking sector carve-out), ROA, D/E (debt-free handling), High Leverage warning flags, Interest Coverage Ratio, Net Debt, and Asset Turnover.
- **Multi-Year CAGR Engine (`src/analytics/cagr.py`)**: Computes 3Y, 5Y, and 10Y Revenue, PAT, and EPS CAGR with 6 edge-case flag handlers (`NORMAL`, `DECLINE_TO_LOSS`, `TURNAROUND`, `BOTH_NEGATIVE`, `ZERO_BASE`, `INSUFFICIENT`).
- **Cash Flow Analytics & Capital Allocation (`src/analytics/cashflow_kpis.py`)**: Calculates Free Cash Flow (FCF), 5-year CFO Quality Score, CapEx Intensity, FCF Conversion Rate, and an 8-pattern Capital Allocation Classifier (`Reinvestor`, `Shareholder Returns`, `Liquidating Assets`, `Distress Signal`, `Growth Funded by Debt`, `Cash Accumulator`, `Pre-Revenue`, `Mixed`).

### 3. Stock Screener & Peer Comparison Engine
- **Customizable Screening Config (`config/screener_config.yaml`)**: Analyst-editable threshold definitions for 6 preset stock screeners across 15 filterable metrics:
  - `Quality Compounder`: High ROE, low debt, positive FCF, strong 5Y Revenue CAGR.
  - `Value Pick`: Low P/E, low P/B, moderate leverage, attractive dividend yield.
  - `Growth Accelerator`: High 5Y PAT and Revenue CAGR with controlled debt.
  - `Dividend Champion`: High dividend yield, sustainable payout ratio, positive FCF.
  - `Debt-Free Blue Chip`: Zero/low debt, strong ROE, large-scale revenue.
  - `Turnaround Watch`: Rebounding 3Y Revenue CAGR, positive FCF, declining leverage.
- **Winsorised Composite Quality Score (0–100)**: Multi-factor score combining 35% Profitability + 30% Cash Quality + 20% Growth + 15% Leverage, with P10/P90 winsorisation and sector-relative scaling.
- **Peer Percentile Rankings (`src/analytics/peer.py`)**: Calculates percentile ranks (`PERCENT_RANK`) across 10 metrics for 11 sector peer groups in SQLite (`peer_percentiles` table). Applies inverted ranking for Debt-to-Equity.
- **Visual Radar Charts (`reports/radar_charts/`)**: Generates 92 polar radar PNG charts comparing company metrics against sector peer averages.
- **Formatted Excel Reports**:
  - `output/screener_output.xlsx`: 6 worksheets with threshold cell formatting.
  - `output/peer_comparison.xlsx`: 11 worksheets with percentile cell formatting and gold-highlighted benchmark rows.

### 4. Quantitative Portfolio Risk & Recommender Engine
- **Risk Metrics**: Computes 95% Historical Value-at-Risk (VaR), Conditional VaR (CVaR), Rolling Sharpe Ratios, Sortino Ratios, Portfolio Beta vs NIFTY 50, and sector Herfindahl-Hirschman Index (HHI) concentration.
- **Automated Portfolio Tools**:
  - Monte Carlo 5-Year NAV Simulator (`scripts/monte_carlo_sim.py`)
  - Markowitz Efficient Frontier Optimizer (`scripts/markowitz_frontier.py`)
  - Cron NAV Scheduler (`scripts/cron_scheduler.py`)
  - Interactive Fund Recommender Engine (`recommender.py`)
  - Automated HTML Email Reporter (`scripts/email_report.py`)

---

## ⚡ Setup & Execution Instructions

### 1. Installation
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
make test        # Executes full 66+ unit test suite across all test modules
make report      # Generates technical PDF reports & presentation deck
make dashboard   # Renders HTML web dashboard & Power BI assets
```

### 3. Automated Verification Audit
Run the automated verification script to audit database tables and output files:
```bash
python3 verify_all_capstone_tasks.py
```

### 4. Interactive Streamlit Web Application
Launch the interactive web application:
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

## 🏷️ Repository Release Info
- **Version**: `v1.0`
- **GitHub Repository**: [https://github.com/DGskywalker/BlueStock](https://github.com/DGskywalker/BlueStock)
