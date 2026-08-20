-- Notebook Exploratory SQL Queries (notebooks/exploratory_queries.sql)
-- 10 Production Analytical SQL Queries executing against nifty100.db

-- Query 1: Total Companies Count Check (Definition of Done: 92)
SELECT COUNT(*) AS total_companies_count FROM companies;

-- Query 2: Foreign Key Integrity Check (PRAGMA foreign_key_check)
PRAGMA foreign_key_check;

-- Query 3: Companies Count Grouped by Sector
SELECT s.sector_name, COUNT(c.company_id) AS company_count, ROUND(AVG(c.face_value), 2) AS avg_face_value
FROM sectors s
LEFT JOIN companies c ON s.sector_id = c.sector_id
GROUP BY s.sector_id, s.sector_name
ORDER BY company_count DESC;

-- Query 4: Top 10 Companies by Latest Sales & Operating Profit Margin (OPM %)
SELECT c.ticker, c.company_name, c.sector, p.year, p.sales, p.operating_profit, p.opm_pct
FROM profitandloss p
JOIN companies c ON p.company_id = c.company_id
WHERE p.year = 2024
ORDER BY p.sales DESC
LIMIT 10;

-- Query 5: Companies with Highest 3-Year Profitability (PAT) Growth
SELECT c.ticker, c.company_name, 
       MIN(p.pat) AS min_pat, MAX(p.pat) AS max_pat,
       ROUND(((MAX(p.pat) - MIN(p.pat)) / MIN(p.pat)) * 100.0, 2) AS pat_growth_pct
FROM profitandloss p
JOIN companies c ON p.company_id = c.company_id
GROUP BY c.company_id, c.ticker, c.company_name
HAVING COUNT(p.year) >= 3 AND MIN(p.pat) > 0
ORDER BY pat_growth_pct DESC
LIMIT 10;

-- Query 6: Balance Sheet Asset Integrity & Solvency Ratios
SELECT c.ticker, c.company_name, b.year, b.total_assets, b.total_liabilities, b.borrowings, b.reserves,
       ROUND((b.borrowings / NULLIF(b.reserves, 0)), 2) AS debt_to_reserve_ratio
FROM balancesheet b
JOIN companies c ON b.company_id = c.company_id
WHERE b.year = 2024
ORDER BY b.total_assets DESC
LIMIT 10;

-- Query 7: Cash Flow Generation vs Net Profit (CFO / PAT Quality Ratio)
SELECT c.ticker, c.company_name, p.year, p.pat, cf.cfo, cf.net_cash_flow,
       ROUND((cf.cfo / NULLIF(p.pat, 0)), 2) AS cfo_to_pat_ratio
FROM profitandloss p
JOIN cashflow cf ON p.company_id = cf.company_id AND p.year = cf.year
JOIN companies c ON p.company_id = c.company_id
WHERE p.year = 2024 AND p.pat > 0
ORDER BY cfo_to_pat_ratio DESC
LIMIT 10;

-- Query 8: Average Valuation Ratios (P/E & P/B) Across Sectors
SELECT c.sector, ROUND(AVG(r.pe_ratio), 2) AS avg_pe, ROUND(AVG(r.pb_ratio), 2) AS avg_pb, ROUND(AVG(r.roe_pct), 2) AS avg_roe
FROM financial_ratios r
JOIN companies c ON r.company_id = c.company_id
WHERE r.year = 2024
GROUP BY c.sector
ORDER BY avg_roe DESC;

-- Query 9: Stock Price Volatility & Trading Volume Leaders (Latest 30 Days)
SELECT c.ticker, c.company_name, 
       ROUND(AVG(sp.close_price), 2) AS avg_close_price,
       ROUND(MAX(sp.high_price) - MIN(sp.low_price), 2) AS price_range,
       SUM(sp.volume) AS total_volume_traded
FROM stock_prices sp
JOIN companies c ON sp.company_id = c.company_id
GROUP BY c.company_id, c.ticker, c.company_name
ORDER BY total_volume_traded DESC
LIMIT 10;

-- Query 10: Multi-Year Coverage Audit Per Company (<5 Years Flag)
SELECT c.company_id, c.ticker, c.company_name, COUNT(DISTINCT p.year) AS historical_years_count
FROM companies c
LEFT JOIN profitandloss p ON c.company_id = p.company_id
GROUP BY c.company_id, c.ticker, c.company_name
ORDER BY historical_years_count ASC, c.ticker ASC;
