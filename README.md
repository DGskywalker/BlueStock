# 📊 BlueStock Mutual Fund Analytics Platform — Capstone Project (v1.0)

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-green.svg)](https://www.sqlite.org/)
[![Power BI](https://img.shields.io/badge/Dashboard-Power%20BI-yellow.svg)](https://powerbi.microsoft.com/)
[![Release](https://img.shields.io/badge/Release-v1.0-brightgreen.svg)](https://github.com/DGskywalker/BlueStock/releases/tag/v1.0)

An end-to-end data engineering, quantitative risk analytics, and executive dashboard platform built for the **Indian Mutual Fund Industry**. The platform automates data ingestion, cleaning, daily NAV holiday forward-filling, SQLite star schema loading (`bluestock_mf.db`), quantitative risk diagnostics (CAGR, Sharpe, Sortino, OLS Alpha/Beta, 95% VaR & CVaR, HHI concentration), composite scorecard modeling (0–100), and renders a 4-page Power BI executive dashboard.

---

## 🚀 Key Deliverables & Manifest

| Deliverable | Location / Path | Description |
| :--- | :--- | :--- |
| **Final Technical Report** | [reports/Final_Report.pdf](file:///Users/divyanshgupta/Desktop/BlueStock/reports/Final_Report.pdf) *(or [Final_Report.pdf](file:///Users/divyanshgupta/Desktop/BlueStock/Final_Report.pdf))* | 15–20 page comprehensive PDF report with ETL architecture, EDA figures, risk tables, and recommendations. |
| **Executive Presentation Deck** | [reports/Bluestock_MF_Presentation.pptx](file:///Users/divyanshgupta/Desktop/BlueStock/reports/Bluestock_MF_Presentation.pptx) *(or [Bluestock_MF_Presentation.pptx](file:///Users/divyanshgupta/Desktop/BlueStock/Bluestock_MF_Presentation.pptx))* | 12-slide executive presentation deck in Bluestock Dark Modern theme. |
| **Power BI Template File** | [bluestock_mf_dashboard.pbix](file:///Users/divyanshgupta/Desktop/BlueStock/bluestock_mf_dashboard.pbix) *(or [dashboard/](file:///Users/divyanshgupta/Desktop/BlueStock/dashboard/))* | Power BI project template with 11 relational data sources, relationships, and 4 page schemas. |
| **Combined Dashboard PDF** | [Dashboard.pdf](file:///Users/divyanshgupta/Desktop/BlueStock/Dashboard.pdf) *(or [dashboard/](file:///Users/divyanshgupta/Desktop/BlueStock/dashboard/))* | 4-page PDF document combining all dashboard page screenshots. |
| **Interactive Web Dashboard** | [dashboard/index.html](file:///Users/divyanshgupta/Desktop/BlueStock/dashboard/index.html) | Responsive HTML5/CSS3 Bluestock web application with tab navigation and KPI cards. |
| **SQLite Star Schema DB** | [bluestock_mf.db](file:///Users/divyanshgupta/Desktop/BlueStock/bluestock_mf.db) | Production SQLite database containing 11 relational tables. |
| **Master Pipeline Engine** | [run_pipeline.py](file:///Users/divyanshgupta/Desktop/BlueStock/run_pipeline.py) | Master execution script executing all 10 pipeline stages sequentially. |
| **Jupyter Notebooks** | [notebooks/EDA_Analysis.ipynb](file:///Users/divyanshgupta/Desktop/BlueStock/notebooks/EDA_Analysis.ipynb)<br>[notebooks/Performance_Analytics.ipynb](file:///Users/divyanshgupta/Desktop/BlueStock/notebooks/Performance_Analytics.ipynb)<br>[notebooks/Advanced_Analytics.ipynb](file:///Users/divyanshgupta/Desktop/BlueStock/notebooks/Advanced_Analytics.ipynb) | Production notebooks containing code, risk tables, and documented markdown insight cells. |
| **Fund Scorecard CSV** | [fund_scorecard.csv](file:///Users/divyanshgupta/Desktop/BlueStock/fund_scorecard.csv) | Composite 0–100 rating scores, ranks, Sharpe, Sortino, Alpha, Beta, and Max DD metrics. |
| **Alpha & Beta CSV** | [alpha_beta.csv](file:///Users/divyanshgupta/Desktop/BlueStock/alpha_beta.csv) | OLS linear regression metrics vs NIFTY 100 benchmark. |
| **VaR & CVaR Report CSV** | [var_cvar_report.csv](file:///Users/divyanshgupta/Desktop/BlueStock/var_cvar_report.csv) | Historical 95% Value-at-Risk & Conditional VaR tail risk metrics across all 40 schemes. |
| **Fund Recommender Engine**| [recommender.py](file:///Users/divyanshgupta/Desktop/BlueStock/recommender.py) | Interactive CLI module recommending top 3 funds per risk appetite (`Low`, `Moderate`, `High`). |

---

## ⚡ Setup & Execution Instructions

### 1. System Requirements & Environment
- Python 3.9+ installed on macOS / Linux / Windows.
- Standard libraries: `pandas`, `numpy`, `matplotlib`, `seaborn`, `plotly`, `sqlalchemy`, `scipy`, `reportlab`, `python-pptx`, `nbformat`.

### 2. Installation
Clone the repository and install required dependencies:
```bash
git clone https://github.com/DGskywalker/BlueStock.git
cd BlueStock
python3 -m pip install -r requirements.txt
```

### 3. Running the Master Pipeline
Execute the master execution script to run all 10 stages end-to-end:
```bash
python3 run_pipeline.py
```

### 4. Interactive Fund Recommender Module
Run the interactive recommender module from terminal:
```bash
python3 recommender.py --risk Moderate
```

---

## 📊 Database & Architecture Overview

### Star Schema Architecture (`bluestock_mf.db`)
- **Dimension Tables**:
  - `dim_fund`: Fund master metadata (amfi_code PK, scheme name, AMC, category, plan, launch date).
  - `dim_date`: Calendar dimension (date PK, year, quarter, month, day, day_of_week, is_weekend).
- **Fact Tables**:
  - `fact_nav`: Daily NAV records (amfi_code FK, date FK, nav).
  - `fact_transactions`: Investor transaction logs (investor_id, amfi_code FK, amount, type, state, age, KYC).
  - `fact_performance`: Fund return & risk diagnostics (CAGRs, Sharpe, Sortino, Alpha, Beta, Max DD).
  - `fact_aum`: AMC monthly AUM trends.
  - `fact_portfolio_holdings`: Stock holding weights & sector disclosures.
  - `fact_category_inflows`, `fact_sip_inflows`, `fact_industry_folio_count`, `fact_benchmark_indices`.

---

## 📈 Power BI Executive Dashboard Structure

- **Page 1 (Industry Overview)**: Total AUM (₹81.4L Cr), Monthly SIP (₹31K Cr), Folios (26.12 Cr), AMC AUM Bar Chart (SBI dominance).
- **Page 2 (Fund Performance)**: Risk vs Return Scatter Plot (3Y CAGR vs Max DD Risk), Top 5 Schemes vs NIFTY 50 Benchmark, Scorecard Table.
- **Page 3 (Investor Analytics)**: Transaction Volume by State, SIP/Lumpsum/Redemption Donut Split, Age Group vs Ticket Size.
- **Page 4 (SIP & Market Trends)**: Dual-Axis Monthly SIP Inflow (Bar) + NIFTY 50 Close (Line), Category Monthly Net Inflow Heatmap Matrix.

---

## 🏷️ Release & Commit Tag
- **Version**: `v1.0`
- **Git Commit**: `"Final: Complete Bluestock MF Capstone"`
- **GitHub Repository**: [https://github.com/DGskywalker/BlueStock](https://github.com/DGskywalker/BlueStock)
