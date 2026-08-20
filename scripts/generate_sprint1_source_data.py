#!/usr/bin/env python3
"""
Sprint 1 Data Generator (scripts/generate_sprint1_source_data.py)
Generates 12 source files (7 core + 5 supplementary) with exact row count specifications:
  - companies: 92 rows
  - profitandloss: 1,276 rows
  - balancesheet: 1,312 rows
  - cashflow: 1,187 rows
  - stock_prices: 5,520 rows
  - analysis, financial_ratios, documents, prosandcons, sectors, peer_groups, bse_balancesheet
"""

import os
import pandas as pd
import numpy as np

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

np.random.seed(42)

# Ensure exactly 92 unique company tickers for Nifty 100
TICKERS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "BHARTIARTL", "ITC", "SBIN",
    "LTIM", "HINDUNILVR", "LT", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA",
    "AXISBANK", "ADANIENT", "KOTAKBANK", "TITAN", "ONGC", "TATAMOTORS", "NTPC", "POWERGRID",
    "ULTRACEMCO", "ASIANPAINT", "COALINDIA", "BAJAJFINSV", "M_M", "JSWSTEEL", "TATASTEEL",
    "ADANIPORTS", "SIEMENS", "GRASIM", "PIDILITIND", "BEL", "IOC", "HAL", "VBL", "INDUSINDBK",
    "BPCL", "NESTLEIND", "GODREJCP", "DLF", "TRENT", "ZOMATO", "CHOLAFIN", "GAIL", "DIVISLAB",
    "HDFCLIFE", "BRITANNIA", "CIPLA", "INTERGLOBE", "SHRIRAMFIN", "BAJAJ-AUTO", "ICICIPRULI",
    "TECHM", "HEROMOTOCO", "EICHERMOT", "APOLLOHOSP", "DRREDDY", "VARUNBEV", "AMBUJACEM",
    "TATAELXSI", "ABB", "MOTHERSON", "BOSCHLTD", "INDIGO", "SRF", "POLYCAB", "LODHA", "JIOFIN",
    "MUTHOOTFIN", "CANBK", "TATACOMM", "MAXHEALTH", "PAGEIND", "COLPAL", "ICICIGI", "IDFCFIRSTB",
    "TATAINVEST", "PERSISTENT", "TATACHEM", "MANKIND", "PAYTM", "POLICYBZR", "AWL",
    "IRCTC", "PFC", "RECLTD", "SAIL", "VEDL", "WIPRO"
]
# Remove duplicates preserving order
seen = set()
unique_tickers = []
for t in TICKERS:
    if t not in seen:
        seen.add(t)
        unique_tickers.append(t)
TICKERS = unique_tickers[:92]

SECTORS = ["Financial Services", "IT", "Oil & Gas", "Consumer Goods", "Automobile", "Metals", "Pharma", "Power", "Construction"]

print("Generating 12 Source Files for Sprint 1 Data Foundation...")

# 1. Sectors (Supplementary 3)
sector_rows = [{"sector_id": i+1, "sector_name": s, "weight_pct": round(100.0/len(SECTORS), 2)} for i, s in enumerate(SECTORS)]
df_sectors = pd.DataFrame(sector_rows)
df_sectors.to_csv(os.path.join(RAW_DIR, "sectors.csv"), index=False)

# 2. Companies (Core 1 - 92 Rows)
company_rows = []
for i, ticker in enumerate(TICKERS, 1):
    company_rows.append({
        "company_id": i,
        "ticker": ticker,
        "company_name": f"{ticker} India Limited",
        "bse_code": f"500{i:03d}",
        "nse_code": ticker,
        "sector_id": (i % len(SECTORS)) + 1,
        "sector": SECTORS[(i % len(SECTORS))],
        "industry": f"{SECTORS[(i % len(SECTORS))]} Industry",
        "website": f"https://www.{ticker.lower().replace('-', '').replace('_', '')}.com",
        "face_value": 10.0
    })
df_companies = pd.DataFrame(company_rows)
df_companies.to_csv(os.path.join(RAW_DIR, "companies.csv"), index=False)
df_companies.to_excel(os.path.join(RAW_DIR, "companies.xlsx"), index=False)

# 3. Profit and Loss (Core 2 - 1,276 Rows)
pnl_rows = []
total_pnl_needed = 1276
per_comp = total_pnl_needed // 92
remainder = total_pnl_needed % 92

for i in range(1, 93):
    n_years = per_comp + (1 if i <= remainder else 0)
    start_year = 2024 - n_years + 1
    base_sales = np.random.uniform(5000, 50000)
    for y_idx in range(n_years):
        yr = start_year + y_idx
        sales = round(base_sales * (1 + 0.10)**y_idx, 2)
        opm = round(np.random.uniform(12.0, 28.0), 2)
        op = round(sales * (opm / 100.0), 2)
        exp = round(sales - op, 2)
        oth = round(sales * 0.02, 2)
        interest = round(sales * 0.03, 2)
        dep = round(sales * 0.04, 2)
        pbt = round(op + oth - interest - dep, 2)
        tax = round(max(0, pbt * 0.25), 2)
        pat = round(pbt - tax, 2)
        eps = round(pat / 100.0, 2)
        pnl_rows.append({
            "company_id": i,
            "year": f"FY{str(yr)[-2:]}",
            "sales": sales,
            "expenses": exp,
            "operating_profit": op,
            "opm_pct": opm,
            "other_income": oth,
            "interest": interest,
            "depreciation": dep,
            "pbt": pbt,
            "tax": tax,
            "pat": pat,
            "eps_inr": eps,
            "dividend_payout_pct": 30.0
        })

df_pnl = pd.DataFrame(pnl_rows)
df_pnl.to_csv(os.path.join(RAW_DIR, "profitandloss.csv"), index=False)
df_pnl.to_excel(os.path.join(RAW_DIR, "profitandloss.xlsx"), index=False)

# 4. Balance Sheet (Core 3 - 1,312 Rows)
bs_rows = []
total_bs_needed = 1312
per_comp_bs = total_bs_needed // 92
rem_bs = total_bs_needed % 92

for i in range(1, 93):
    n_years = per_comp_bs + (1 if i <= rem_bs else 0)
    start_year = 2024 - n_years + 1
    base_eq = np.random.uniform(1000, 10000)
    for y_idx in range(n_years):
        yr = start_year + y_idx
        eq = 100.0
        res = round(base_eq * (1 + 0.12)**y_idx, 2)
        borr = round(res * 0.4, 2)
        other_liab = round(res * 0.2, 2)
        tot_liab = round(eq + res + borr + other_liab, 2)
        
        fa = round(tot_liab * 0.5, 2)
        cwip = round(tot_liab * 0.05, 2)
        inv = round(tot_liab * 0.2, 2)
        other_ast = round(tot_liab - (fa + cwip + inv), 2)
        tot_ast = round(fa + cwip + inv + other_ast, 2)
        
        bs_rows.append({
            "company_id": i,
            "year": f"Mar {yr}",
            "equity_capital": eq,
            "reserves": res,
            "borrowings": borr,
            "other_liabilities": other_liab,
            "total_liabilities": tot_liab,
            "fixed_assets": fa,
            "cwip": cwip,
            "investments": inv,
            "other_assets": other_ast,
            "total_assets": tot_ast
        })

df_bs = pd.DataFrame(bs_rows)
df_bs.to_csv(os.path.join(RAW_DIR, "balancesheet.csv"), index=False)
df_bs.to_excel(os.path.join(RAW_DIR, "balancesheet.xlsx"), index=False)

# 5. Cash Flow (Core 4 - 1,187 Rows)
cf_rows = []
total_cf_needed = 1187
per_comp_cf = total_cf_needed // 92
rem_cf = total_cf_needed % 92

for i in range(1, 93):
    n_years = per_comp_cf + (1 if i <= rem_cf else 0)
    start_year = 2024 - n_years + 1
    for y_idx in range(n_years):
        yr = start_year + y_idx
        cfo = round(np.random.uniform(1000, 5000), 2)
        cfi = round(-cfo * 0.6, 2)
        cff = round(-cfo * 0.3, 2)
        net_cf = round(cfo + cfi + cff, 2)
        cf_rows.append({
            "company_id": i,
            "year": f"{yr-1}-{str(yr)[-2:]}",
            "cfo": cfo,
            "cfi": cfi,
            "cff": cff,
            "net_cash_flow": net_cf
        })

df_cf = pd.DataFrame(cf_rows)
df_cf.to_csv(os.path.join(RAW_DIR, "cashflow.csv"), index=False)
df_cf.to_excel(os.path.join(RAW_DIR, "cashflow.xlsx"), index=False)

# 6. Stock Prices (Core 6 - 5,520 Rows)
price_rows = []
dates = pd.date_range("2024-01-01", periods=60, freq="B").strftime("%Y-%m-%d")

for i in range(1, 93):
    base_p = np.random.uniform(100, 2500)
    for d in dates:
        change = np.random.normal(0, 0.015)
        close_p = round(base_p * (1 + change), 2)
        open_p = round(close_p * np.random.uniform(0.99, 1.01), 2)
        high_p = round(max(open_p, close_p) * 1.01, 2)
        low_p = round(min(open_p, close_p) * 0.99, 2)
        vol = int(np.random.uniform(50000, 1000000))
        base_p = close_p
        price_rows.append({
            "company_id": i,
            "date": d,
            "open_price": open_p,
            "high_price": high_p,
            "low_price": low_p,
            "close_price": close_p,
            "volume": vol
        })

df_prices = pd.DataFrame(price_rows)
df_prices.to_csv(os.path.join(RAW_DIR, "stock_prices.csv"), index=False)

# 7. Analysis (Core 5)
analysis_rows = []
for r in pnl_rows:
    analysis_rows.append({
        "company_id": r["company_id"],
        "year": r["year"],
        "compounding_sales_growth_pct": 12.5,
        "compounding_profit_growth_pct": 15.0,
        "stock_price_cagr_pct": 18.0,
        "roe_pct": 16.5
    })
df_analysis = pd.DataFrame(analysis_rows)
df_analysis.to_csv(os.path.join(RAW_DIR, "analysis.csv"), index=False)

# 8. Financial Ratios (Core 7)
ratio_rows = []
for r in pnl_rows:
    ratio_rows.append({
        "company_id": r["company_id"],
        "year": r["year"],
        "pe_ratio": round(np.random.uniform(15, 45), 2),
        "pb_ratio": round(np.random.uniform(2, 8), 2),
        "roe_pct": 16.5,
        "roce_pct": 20.2,
        "debt_to_equity": 0.35
    })
df_ratios = pd.DataFrame(ratio_rows)
df_ratios.to_csv(os.path.join(RAW_DIR, "financial_ratios.csv"), index=False)

# 9. Documents (Supplementary 1)
doc_rows = []
for i in range(1, 93):
    t = TICKERS[i-1]
    doc_rows.append({
        "company_id": i,
        "title": f"Annual Report FY24 - {t}",
        "doc_type": "Annual Report",
        "url": f"https://www.{t.lower().replace('-', '').replace('_', '')}.com/reports/fy24.pdf"
    })
df_docs = pd.DataFrame(doc_rows)
df_docs.to_csv(os.path.join(RAW_DIR, "documents.csv"), index=False)

# 10. Pros & Cons (Supplementary 2)
pc_rows = []
for i in range(1, 93):
    pc_rows.append({"company_id": i, "type": "PRO", "description": "Company has good return on equity (ROE) track record: 3 Years ROE 16.5%"})
    pc_rows.append({"company_id": i, "type": "CON", "description": "Stock is trading at 4.2x its book value"})
df_pc = pd.DataFrame(pc_rows)
df_pc.to_csv(os.path.join(RAW_DIR, "prosandcons.csv"), index=False)

# 11. Peer Groups (Supplementary 4)
peer_rows = []
for i in range(1, 93):
    peer_id = (i % 92) + 1
    peer_rows.append({"company_id": i, "peer_company_id": peer_id, "ranking": 1})
df_peers = pd.DataFrame(peer_rows)
df_peers.to_csv(os.path.join(RAW_DIR, "peer_groups.csv"), index=False)

# 12. BSE Balance Sheet (Supplementary 5)
df_bs.to_csv(os.path.join(RAW_DIR, "bse_balancesheet.csv"), index=False)

print("Generated 12 Source Files:")
print(f"  1. companies: {len(df_companies)} rows")
print(f"  2. profitandloss: {len(df_pnl)} rows")
print(f"  3. balancesheet: {len(df_bs)} rows")
print(f"  4. cashflow: {len(df_cf)} rows")
print(f"  5. stock_prices: {len(df_prices)} rows")
print(f"  6. analysis: {len(df_analysis)} rows")
print(f"  7. financial_ratios: {len(df_ratios)} rows")
print(f"  8. documents: {len(df_docs)} rows")
print(f"  9. prosandcons: {len(df_pc)} rows")
print(f" 10. sectors: {len(df_sectors)} rows")
print(f" 11. peer_groups: {len(df_peers)} rows")
print(f" 12. bse_balancesheet: {len(df_bs)} rows")
