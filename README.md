# 📊 BlueStock Financial Analytics & Equity Research Platform

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Web%20App-Streamlit-red.svg)](https://streamlit.io/)
[![Unit Tests](https://img.shields.io/badge/Tests-80%2B%20Passed-brightgreen.svg)](https://github.com/DGskywalker/BlueStock)
[![Release](https://img.shields.io/badge/Release-v1.0-brightgreen.svg)](https://github.com/DGskywalker/BlueStock/releases/tag/v1.0)

An end-to-end data engineering, equity research, financial ratio calculation engine, quantitative valuation engine, NLP text parser, cash flow intelligence module, ReportLab PDF tearsheet engine, KMeans clustering module, 16-endpoint FastAPI REST API server, and 8-screen interactive web dashboard built for **Bluestock Fintech**.

The platform automates raw financial data ingestion, executes 16 data quality validation rules, loads a relational SQLite database (`nifty100.db` & `bluestock_mf.db`), calculates 50+ financial ratios, handles multi-year CAGR edge cases, classifies capital allocation patterns, powers 6 preset stock screeners, evaluates 11 peer group percentile rankings, renders 92 polar radar visualizations, computes FCF Yield and overvaluation flags (`Caution`, `Discount`, `Fair`), parses CAGR text using regex, generates 24 rule-based pros and cons with confidence scores (>60%), classifies CFO quality and distress signals, batch renders 92 2-page company PDF tearsheets and 11 sector PDF reports, runs KMeans clustering ($k=5$) for archetype discovery, exposes a 16-endpoint FastAPI REST API with OpenAPI documentation, models mutual fund risk (VaR, CVaR, Sharpe, Beta), and serves an 8-screen interactive Streamlit web dashboard.

---

## 📌 System Architecture

```
BlueStock Platform Architecture
├── 1. Data Foundation & ETL ---------> Relational SQLite Database (nifty100.db, 16 DQ Rules)
├── 2. Financial Ratio Engine ---------> 50+ KPIs, 8-Pattern Capital Allocation Classifier
├── 3. Stock Screener & Peer Engine ---> 6 Presets, Winsorised Composite Quality Score, 92 Radar PNGs
├── 4. Valuation Analytics Engine ----> FCF Yield, Sector Median P/E, Caution/Discount Overvaluation Flags
├── 5. Cash Flow & NLP Engine ---------> Regex Analysis Text Parser, 24 Auto Pros/Cons Rules (>60% Confidence)
├── 6. PDF Report Generation Engine ----> 92 Company PDF Tearsheets, 11 Sector PDFs, Portfolio Summary PDF
├── 7. KMeans Clustering Module -------> k=5 Archetype Segmentation, Outlier Detection & Inertia Elbow Plot
├── 8. REST API Engine (FastAPI) ------> 16 Endpoint REST Server with OpenAPI Specification (docs/openapi.json)
├── 9. 8-Screen Web Dashboard ---------> Multi-Page Streamlit App (streamlit run app.py)
└── 10. Build & QA Automation ---------> Makefile Automation, HTML Test Audit Report & 80+ Unit Tests
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

### 3. Cash Flow Intelligence & Capital Allocation (`src/analytics/cashflow_kpis.py`)
- **CFO Quality Score**: Calculates 5-year average CFO/PAT ratio and labels companies as `High Quality` (>1.0), `Moderate` (0.5-1.0), or `Accrual Risk` (<0.5).
- **CapEx Intensity %**: Computes CapEx Intensity % (`abs(investing_activity) / sales * 100`) labeled as `Asset Light` (<3%), `Moderate` (3-8%), or `Capital Intensive` (>8%).
- **Distress Signal & Deleveraging Flags**: Identifies operational distress ($CFO < 0 \land CFF > 0$) and debt payoff activity ($CFF < 0 \land \text{borrowings declining}$).
- **Capital Allocation Classifier**: Categorizes companies into 8 capital allocation patterns (`Reinvestor`, `Shareholder Returns`, `Liquidating Assets`, `Distress Signal`, `Growth Funded by Debt`, `Cash Accumulator`, `Pre-Revenue`, `Mixed`).
- **Outputs**: `output/cashflow_intelligence.xlsx` (92 rows), `output/distress_alerts.csv`, and `output/pattern_changes.csv`.

### 4. Stock Screener & Peer Comparison Engine
- **Customizable Screening Config (`config/screener_config.yaml`)**: Analyst-editable threshold definitions for 6 preset stock screeners across 15 filterable metrics (`Quality Compounder`, `Value Pick`, `Growth Accelerator`, `Dividend Champion`, `Debt-Free Blue Chip`, `Turnaround Watch`).
- **Winsorised Composite Quality Score (0–100)**: Multi-factor score combining 35% Profitability + 30% Cash Quality + 20% Growth + 15% Leverage, with P10/P90 winsorisation and sector-relative scaling.
- **Peer Percentile Rankings (`src/analytics/peer.py`)**: Calculates percentile ranks (`PERCENT_RANK`) across 10 metrics for 11 sector peer groups in SQLite (`peer_percentiles` table).
- **Visual Radar Charts (`reports/radar_charts/`)**: Generates 92 polar radar PNG charts comparing company metrics against sector peer averages.

### 5. Valuation Analytics Engine (`src/analytics/valuation.py`)
- **FCF Yield Calculation**: Computes FCF Yield (`FCF / Market Cap * 100`) for all 92 companies.
- **Sector Median P/E & Overvaluation Classification**:
  - `Caution` (Overvalued): $P/E > 1.5 \times \text{Sector Median P/E}$
  - `Discount` (Undervalued): $P/E < 0.7 \times \text{Sector Median P/E}$
  - `Fair`: Otherwise
- **Outputs**: `output/valuation_summary.xlsx` (92 rows) and `output/valuation_flags.csv`.

### 6. NLP Analysis Parser & Auto Pros/Cons Generator (`src/nlp/`)
- **Regex Text Parser (`src/nlp/parser.py`)**: Parses text fields in `analysis.xlsx` using `(\d+)\s*Years?:?\s*([\d.]+)%` to extract period and CAGR values (`output/analysis_parsed.csv`).
- **Auto Pros/Cons Generator (`src/nlp/pros_cons_generator.py`)**: Evaluates 12 Pro rules and 12 Con rules across financial metrics, assigns confidence scores (>60%), and exports `output/pros_cons_generated.csv`, ensuring every company has at least 1 pro and at least 1 con.

### 7. ReportLab PDF Reports Engine (`src/reports/`)
- **Company Tearsheets (`reports/tearsheets/`)**: Batch generates 92 2-page company tearsheet PDFs with navy header bar, 6 KPI tiles, revenue/PAT bar chart, ROE/ROCE line chart, balance sheet composition, cash flow waterfall, and pros/cons bullets.
- **Sector PDF Reports (`reports/sector/`)**: Batch generates 11 sector PDF reports with sector median KPIs and company metric lists.
- **Portfolio Summary PDF (`reports/portfolio/portfolio_summary.pdf`)**: 92-page PDF report sorted alphabetically by ticker with top 6 KPIs and YoY trend arrows.

### 8. KMeans Clustering Module (`src/analytics/clustering.py`)
- **Feature Standardisation**: Imputes sector medians for missing data and standardises 5 core features (`ROE %`, `D/E`, `Revenue 5Y CAGR`, `FCF 5Y CAGR`, `OPM %`) using `StandardScaler`.
- **Optimal Cluster Selection ($k=5$)**: Evaluates inertia across $k=2\dots10$, generating the elbow plot (`reports/elbow_plot.png`) to confirm $k=5$ as optimal.
- **Archetype Segmentation**: Segments companies into 5 distinct clusters (`High-Margin Quality Compounders`, `Capital-Intensive Growth`, `Stagnant / Turnaround Candidates`, `Moderate Leverage Stable Earners`, `High-Debt High-Growth Speculative`).
- **Outputs**: `output/cluster_labels.csv`, `reports/elbow_plot.png`, `reports/correlation_heatmap.png`, `output/outlier_report.csv`, and `output/portfolio_stats.csv`.

### 9. FastAPI REST API Server (`src/api/main.py`)
- **16 REST Endpoints**: Implements 7 modular router packages (`companies.py`, `screener.py`, `sectors.py`, `peers.py`, `valuation.py`, `portfolio.py`, `health.py`).
- **OpenAPI Specification**: Interactive Swagger documentation available at `http://localhost:8000/docs` and exported to `docs/openapi.json`.
- **Features**: Filtering by metric thresholds, company financial lookups, sector benchmarks, valuation signals, and portfolio analytics.

### 10. Interactive 8-Screen Streamlit Web Dashboard (`src/dashboard/app.py` & `pages/`)
Launch using `streamlit run app.py` or `make dashboard`:
1. **Home Overview (`pages/01_home.py`)**: Top 6 summary KPI tiles, Plotly sector breakdown donut chart, top 5 quality companies table, sidebar year filter.
2. **Company 360° Profile (`pages/02_profile.py`)**: Autocomplete search, company metadata card, 6 KPI cards, 10-year Revenue & Net Profit bar chart, ROE/ROCE line chart, Pros & Cons badges.
3. **Interactive Stock Screener (`pages/03_screener.py`)**: 10 metric sliders, 6 preset buttons, live filtered results table, result count label, and CSV export download button.
4. **Peer Analytics & Benchmarks (`pages/04_peers.py`)**: 11 peer group dropdown, 8-axis Plotly polar radar chart, side-by-side KPI comparison table with gold benchmark highlights.
5. **Multi-Metric Trend Analysis (`pages/05_trends.py`)**: Overlay up to 3 financial metrics over 10 years with YoY % growth annotations.
6. **Sector Deep Dive (`pages/06_sectors.py`)**: Sector dropdown, bubble scatter chart (Revenue vs ROE vs Market Cap), sector median bar chart.
7. **Capital Allocation Map (`pages/07_capital.py`)**: Plotly Treemap of 92 companies grouped by 8 capital allocation patterns with interactive company list.
8. **Annual Reports Filing Repository (`pages/08_reports.py`)**: Company document search, BSE PDF download links, and fallback status badges.

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
make nlp         # Executes NLP Parser & Auto Pros/Cons Generator
make pdfs        # Batch generates 92 company tearsheet PDFs & 11 sector PDF reports
make cluster     # Runs KMeans clustering (k=5), generates elbow plot & correlation heatmap
make api         # Launches FastAPI REST Server on http://localhost:8000
make test        # Executes 80+ unit/API tests & generates reports/pytest_report.html
make dashboard   # Launches interactive Streamlit web application on http://localhost:8501
make report      # Generates technical PDF reports & presentation deck
make clean       # Cleans python cache and temporary test artifacts
```

### 3. Running the REST API Server
```bash
make api
# Interactive API Docs available at http://localhost:8000/docs
```

### 4. Running the Streamlit Web Application
```bash
make dashboard
# Dashboard available at http://localhost:8501
```

### 5. Automated Verification Audit
```bash
python3 verify_all_capstone_tasks.py
```

---

## 🧪 Unit Test Suite Verification (80+ Unit & API Tests)

```bash
=== Running All Unit & API Test Suites (80+ Tests across ETL, KPI, Screener, Peer, Valuation, NLP, Reports & API) ===
python3 scripts/generate_test_report.py
```

| Test Suite Module | Directory Path | Tests Executed | Passed | Failed | Errors | Duration | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **ETL Pipeline** | `tests/etl` | 35 | 35 | 0 | 0 | 0.028s | **PASSED** |
| **KPI Analytics Engine** | `tests/kpi` | 23 | 23 | 0 | 0 | 7.041s | **PASSED** |
| **Stock Screener Engine** | `tests/screener` | 5 | 5 | 0 | 0 | 0.354s | **PASSED** |
| **Peer Comparison Analytics** | `tests/peer` | 3 | 3 | 0 | 0 | 0.426s | **PASSED** |
| **Valuation Engine** | `tests/valuation` | 4 | 4 | 0 | 0 | 0.276s | **PASSED** |
| **NLP & Pros/Cons Engine** | `tests/nlp` | 3 | 3 | 0 | 0 | 0.266s | **PASSED** |
| **Report Generators** | `tests/reports` | 2 | 2 | 0 | 0 | 0.632s | **PASSED** |
| **FastAPI REST Server** | `tests/api` | 5 | 5 | 0 | 0 | 0.494s | **PASSED** |

HTML test report auto-generated at `reports/pytest_report.html`.

---

## 🏷️ Deliverables & Release Info
- **Version**: `v1.0`
- **GitHub Repository**: [https://github.com/DGskywalker/BlueStock](https://github.com/DGskywalker/BlueStock)
- **Deliverables**: 23 core artifacts (`output/`, `reports/`, `docs/`, `data/`) fully verified and archived.
