-- ============================================================================
-- BlueStock Mutual Fund Platform - 10 Analytical SQL Queries
-- Database: bluestock_mf.db
-- ============================================================================

-- Query 1: Top 5 Funds by AUM (Assets Under Management)
-- Purpose: Identify the largest mutual fund schemes by AUM size.
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    p.aum_crore,
    p.expense_ratio_pct
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- Query 2: Average NAV per Month by Fund Category
-- Purpose: Track monthly NAV movements and trend benchmarks across asset categories.
SELECT 
    f.category,
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS avg_nav,
    MIN(n.nav) AS min_nav,
    MAX(n.nav) AS max_nav
FROM fact_nav n
JOIN dim_fund f ON n.amfi_code = f.amfi_code
JOIN dim_date d ON n.date = d.date
GROUP BY f.category, d.year, d.month, d.month_name
ORDER BY f.category, d.year, d.month;


-- Query 3: Monthly SIP Inflows & YoY Growth Trends
-- Purpose: Analyze retail investor participation trends, active SIP accounts, and YoY growth.
SELECT 
    month,
    sip_inflow_crore,
    active_sip_accounts_crore,
    new_sip_accounts_lakh,
    sip_aum_lakh_crore,
    COALESCE(ROUND(yoy_growth_pct, 2), 0.0) AS yoy_growth_pct
FROM fact_sip_inflows
ORDER BY month ASC;


-- Query 4: Investor Transaction Volume & Amount by State and City Tier
-- Purpose: Understand geographic distribution of mutual fund investments and redemption patterns.
SELECT 
    t.state,
    t.city_tier,
    COUNT(t.transaction_id) AS total_transactions,
    COUNT(DISTINCT t.investor_id) AS unique_investors,
    SUM(t.amount_inr) AS gross_transaction_amount_inr,
    SUM(t.net_amount_inr) AS net_cash_flow_inr
FROM fact_transactions t
GROUP BY t.state, t.city_tier
ORDER BY gross_transaction_amount_inr DESC
LIMIT 10;


-- Query 5: Funds with Expense Ratio < 1.0% (Low-Cost Funds)
-- Purpose: Highlight cost-effective schemes with lower expense ratios for investors.
SELECT 
    f.amfi_code,
    f.scheme_name,
    f.fund_house,
    f.category,
    f.plan,
    p.expense_ratio_pct,
    p.return_3yr_pct,
    p.alpha,
    p.morningstar_rating
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;


-- Query 6: Top 10 Schemes Ranked by Sharpe & Risk-Adjusted Performance
-- Purpose: Rank funds by risk-adjusted return (Sharpe Ratio, Sortino Ratio, and Alpha).
SELECT 
    f.scheme_name,
    f.fund_house,
    f.category,
    f.sub_category,
    p.sharpe_ratio,
    p.sortino_ratio,
    p.alpha,
    p.return_3yr_pct,
    p.risk_grade
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY p.sharpe_ratio DESC
LIMIT 10;


-- Query 7: Monthly Category Net Inflows Breakdown
-- Purpose: Track capital allocation preferences across Small Cap, Mid Cap, Large Cap, Flexi Cap, etc.
SELECT 
    month,
    category,
    net_inflow_crore
FROM fact_category_inflows
ORDER BY month DESC, net_inflow_crore DESC;


-- Query 8: Top Stock Holdings Across All Portfolio Funds
-- Purpose: Identify the most heavily invested stocks by total market value across all funds.
SELECT 
    h.stock_symbol,
    h.stock_name,
    h.sector,
    COUNT(DISTINCT h.amfi_code) AS fund_count,
    ROUND(SUM(h.market_value_cr), 2) AS total_market_val_cr,
    ROUND(AVG(h.weight_pct), 2) AS avg_portfolio_weight_pct
FROM fact_portfolio_holdings h
GROUP BY h.stock_symbol, h.stock_name, h.sector
ORDER BY total_market_val_cr DESC
LIMIT 10;


-- Query 9: KYC Verification Status & Payment Mode Inflow Analysis
-- Purpose: Evaluate KYC compliance rates and digital vs traditional payment channel adoption.
SELECT 
    t.kyc_status,
    t.payment_mode,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.amount_inr) AS total_amount_inr,
    ROUND(AVG(t.amount_inr), 2) AS avg_transaction_amount_inr
FROM fact_transactions t
GROUP BY t.kyc_status, t.payment_mode
ORDER BY transaction_count DESC;


-- Query 10: Benchmark Index Correlation & Scheme Alpha Outperformance
-- Purpose: Compare scheme 3-year CAGR returns against benchmark returns to measure outperformance (Alpha).
SELECT 
    f.scheme_name,
    f.benchmark,
    p.return_3yr_pct AS scheme_3yr_return,
    p.benchmark_3yr_pct AS benchmark_3yr_return,
    ROUND(p.return_3yr_pct - p.benchmark_3yr_pct, 2) AS excess_return_pct,
    p.alpha,
    p.beta
FROM dim_fund f
JOIN fact_performance p ON f.amfi_code = p.amfi_code
ORDER BY excess_return_pct DESC;
