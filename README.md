# 📊 BlueStock Financial Analytics & Equity Research Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-yellow.svg)](https://powerbi.microsoft.com/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red.svg)](https://streamlit.io/)
[![Unit Tests](https://img.shields.io/badge/Tests-70%20Passed-brightgreen.svg)](https://github.com/DGskywalker/BlueStock)
[![Release](https://img.shields.io/badge/Release-v1.0-brightgreen.svg)](https://github.com/DGskywalker/BlueStock/releases/tag/v1.0)

An end-to-end data engineering, equity research, financial ratio calculation engine, quantitative valuation engine, risk analytics, and 8-screen interactive web dashboard built for **Bluestock Fintech**.

The platform automates raw financial data ingestion, executes 16 data quality validation rules, loads a relational SQLite database (`nifty100.db` & `bluestock_mf.db`), calculates 50+ financial ratios, handles multi-year CAGR edge cases, classifies capital allocation patterns, powers 6 preset stock screeners, evaluates 11 peer group percentile rankings, renders 92 polar radar visualizations, computes FCF Yield and overvaluation flags (`Caution`, `Discount`, `Fair`), models mutual fund risk (VaR, CVaR, Sharpe, Beta), and serves an 8-screen interactive Streamlit web dashboard and executive PDF reporting engines.

---

## 📌 System Architecture

```
BlueStock Platform Architecture
├── 1. Data Foundation & ETL ---------> Relational SQLite Database (nifty100.db, 16 DQ Rules)
├── 2. Financial Ratio Engine ---------> 50+ KPIs, 8-Pattern Capital Allocation Classifier
├── 3. Stock Screener & Peer Engine ---> 6 Presets, Winsorised Composite Quality Score, 92 Radar PNGs
├── 4. Valuation Analytics Engine ----> FCF Yield, Sector Median P/E, Caution/Discount Overvaluation Flags
├── 5. 8-Screen Web Dashboard ---------> Multi-Page Streamlit App (streamlit run app.py) & Power BI
└── 6. Build & Automation -------------> Makefile Build Targets & Automated Unit Test Suite (70 Tests)
```

---

## 🚀 Key Modules & Features

### 1. Data Foundation & Ingestion Engine
- **Relational SQLite Database (`nifty100.db`)**: 10 relational tables (`companies`, `profitandloss`, `balancesheet`, `cashflow`, `financial_ratios`, `analysis`, `documents`, `prosandcons`, `sectors`, `stock_prices`, `peer_groups`).
- **Data Quality Validator (`src/etl/validator.py`)**: 16 automated validation rules covering primary key uniqueness, foreign key integrity, balance sheet balancing, OPM cross-checks, tax rate bounds, URL formatting, and price outlier detection.
- **ETL Loader & Normaliser (`src/etl/loader.py` & `src/etl/normaliser.py`)**: Standardises financial year formats and ticker symbols across incoming source files.

### 2. Financial Ratio & Analytics Engine
- **Profitability, Leverage & Efficiency (`src/analytics/ratios.py`)**: Computes NPM, OPM cross-checks, ROE (with negative equity handling), ROCE (with banking sector carve-out), ROA, D/E (debt-free handling), High Leverage warning flags, Interest Coverage Ratio, Net Debt, and Asset Turnover.
- **Multi-Year CAGR Engine (`src/analytics/cagr.py`)**: Computes 3Y, 5Y, and 10Y Revenue, PAT, and EPS CAGR with 6 edge-case flag handlers (`NORMAL`, `DECLINE_TO_LOSS`, `TURNAROUND`, `BOTH_NEGATIVE`, `ZERO_BASE`, `INSUFFICIENT`).
- **Cash Flow Analytics & Capital Allocation (`src/analytics/cashflow_kpis.py`)**: Calculates Free Cash Flow (FCF), 5-year CFO Quality Score, CapEx Intensity, FCF Conversion Rate, and an 8-pattern Capital Allocation Classifier (`Reinvestor`, `Shareholder Returns`, `Liquidating Assets`, `Distress Signal`, `Growth Funded by Debt`, `Cash Accumulator`, `Pre-Revenue`, `Mixed`).

### 3. Stock Screener & Peer Comparison Engine
- **Customizable Screening Config (`config/screener_config.yaml`)**: Analyst-editable threshold definitions for 6 preset stock screeners across 15 filterable metrics (`Quality Compounder`, `Value Pick`, `Growth Accelerator`, `Dividend Champion`, `Debt-Free Blue Chip`, `Turnaround Watch`).
- **Winsorised Composite Quality Score (0–100)**: Multi-factor score combining 35% Profitability + 30% Cash Quality + 20% Growth + 15% Leverage, with P10/P90 winsorisation and sector-relative scaling.
- **Peer Percentile Rankings (`src/analytics/peer.py`)**: Calculates percentile ranks (`PERCENT_RANK`) across 10 metrics for 11 sector peer groups in SQLite (`peer_percentiles` table). Applies inverted ranking for Debt-to-Equity.
- **Visual Radar Charts (`reports/radar_charts/`)**: Generates 92 polar radar PNG charts comparing company metrics against sector peer averages.

### 4. Valuation Analytics Engine (`src/analytics/valuation.py`)
- **FCF Yield Calculation**: Computes FCF Yield (`FCF / Market Cap * 100`) for all 92 companies.
- **Sector Median P/E & Overvaluation Classification**:
  - `Caution` (Overvalued): $P/E > 1.5 \times \text{Sector Median P/E}$
  - `Discount` (Undervalued): $P/E < 0.7 \times \text{Sector Median P/E}$
  - `Fair`: Otherwise
- **Outputs**:
  - `output/valuation_summary.xlsx`: 92 rows with P/E, P/B, EV/EBITDA, FCF Yield %, 5Y Median P/E, Sector Median P/E %, and Overvaluation Flags.
  - `output/valuation_flags.csv`: Filtered report of Caution & Discount flagged companies.

### 5. Interactive 8-Screen Streamlit Web Dashboard (`src/dashboard/app.py` & `pages/`)
Launch using `streamlit run app.py` or `streamlit run src/dashboard/app.py`:
1. **Home Overview (`pages/01_home.py`)**: Top 6 summary KPI tiles, Plotly sector breakdown donut chart, top 5 quality companies table, sidebar year filter (2019 to 2024).
2. **Company 360° Profile (`pages/02_profile.py`)**: Autocomplete search, company metadata card, 6 KPI cards, 10-year Revenue & Net Profit bar chart, ROE/ROCE line chart, Pros & Cons badges.
3. **Interactive Stock Screener (`pages/03_screener.py`)**: 10 metric sliders, 6 preset buttons, live filtered results table, result count label, and CSV export download button.
4. **Peer Analytics & Benchmarks (`pages/04_peers.py`)**: 11 peer group dropdown, 8-axis Plotly polar radar chart, side-by-side KPI comparison table with gold benchmark highlights.
5. **Multi-Metric Trend Analysis (`pages/05_trends.py`)**: Overlay up to 3 financial metrics over 10 years with YoY % growth annotations.
6. **Sector Deep Dive (`pages/06_sectors.py`)**: Sector dropdown, bubble scatter chart (Revenue vs ROE vs Market Cap), sector median bar chart.
7. **Capital Allocation Map (`pages/07_capital.py`)**: Plotly Treemap of 92 companies grouped by 8 capital allocation patterns with interactive company list.
8. **Annual Reports Filing Repository (`pages/08_reports.py`)**: Company document search, BSE PDF download links, and red `"Report unavailable"` fallback status badges.

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
make valuation   # Executes Valuation Engine (output/valuation_summary.xlsx & valuation_flags.csv)
make test        # Executes 70+ unit tests across tests/etl, tests/kpi, tests/screener, tests/peer, tests/valuation
make dashboard   # Launches interactive Streamlit web application on localhost:8501
make report      # Generates technical PDF reports & presentation deck
```

### 3. Running the Streamlit Web Application
```bash
streamlit run app.py
```

### 4. Automated Verification Audit
```bash
python3 verify_all_capstone_tasks.py
```

---

## 🧪 Unit Test Suite Verification (70 Unit Tests)

```bash
=== Running All Unit Test Suites (70+ Unit Tests across ETL, KPI, Screener, Peer & Valuation) ===
python3 -m unittest discover -s tests/etl -p "test_*.py"       # 35 Passed in 0.008s - OK
python3 -m unittest discover -s tests/kpi -p "test_*.py"       # 23 Passed in 0.081s - OK
python3 -m unittest discover -s tests/screener -p "test_*.py"  #  5 Passed in 1.603s - OK
python3 -m unittest discover -s tests/peer -p "test_*.py"      #  3 Passed in 0.057s - OK
python3 -m unittest discover -s tests/valuation -p "test_*.py" #  4 Passed in 0.160s - OK
```

---

## 🏷️ Repository Release Info
- **Version**: `v1.0`
- **GitHub Repository**: [https://github.com/DGskywalker/BlueStock](https://github.com/DGskywalker/BlueStock)
