-- SQLite Star Schema DDL Script for BlueStock Mutual Fund Platform
-- Database: bluestock_mf.db

PRAGMA foreign_keys = ON;

-- ============================================================================
-- DIMENSION TABLES
-- ============================================================================

-- 1. Dimension: Fund Master
DROP TABLE IF EXISTS dim_fund;
CREATE TABLE dim_fund (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT NOT NULL,
    sub_category        TEXT NOT NULL,
    plan                TEXT NOT NULL,
    launch_date         TEXT,
    benchmark           TEXT,
    expense_ratio_pct   REAL,
    exit_load_pct       REAL,
    min_sip_amount      INTEGER,
    min_lumpsum_amount  INTEGER,
    fund_manager        TEXT,
    risk_category       TEXT,
    sebi_category_code  TEXT
);

-- 2. Dimension: Date Calendar
DROP TABLE IF EXISTS dim_date;
CREATE TABLE dim_date (
    date                TEXT PRIMARY KEY, -- YYYY-MM-DD
    year                INTEGER NOT NULL,
    quarter             INTEGER NOT NULL,
    month               INTEGER NOT NULL,
    month_name          TEXT NOT NULL,
    day                 INTEGER NOT NULL,
    day_of_week         INTEGER NOT NULL,
    is_weekend          INTEGER NOT NULL -- 1 if Saturday/Sunday else 0
);

-- ============================================================================
-- FACT TABLES
-- ============================================================================

-- 3. Fact: Daily NAV History
DROP TABLE IF EXISTS fact_nav;
CREATE TABLE fact_nav (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    date                TEXT NOT NULL,
    nav                 REAL NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date (date)
);

-- 4. Fact: Investor Transactions
DROP TABLE IF EXISTS fact_transactions;
CREATE TABLE fact_transactions (
    transaction_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id         TEXT NOT NULL,
    transaction_date    TEXT NOT NULL,
    amfi_code           INTEGER NOT NULL,
    transaction_type    TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount_inr          INTEGER NOT NULL,
    net_amount_inr      INTEGER NOT NULL, -- Signed amount (Negative for Redemptions)
    state               TEXT,
    city                TEXT,
    city_tier           TEXT,
    age_group           TEXT,
    gender              TEXT,
    annual_income_lakh  REAL,
    payment_mode        TEXT,
    kyc_status          TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date (date)
);

-- 5. Fact: Scheme Performance Metrics
DROP TABLE IF EXISTS fact_performance;
CREATE TABLE fact_performance (
    amfi_code           INTEGER PRIMARY KEY,
    scheme_name         TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    category            TEXT NOT NULL,
    plan                TEXT NOT NULL,
    return_1yr_pct      REAL,
    return_3yr_pct      REAL,
    return_5yr_pct      REAL,
    benchmark_3yr_pct   REAL,
    alpha               REAL,
    beta                REAL,
    sharpe_ratio        REAL,
    sortino_ratio       REAL,
    std_dev_ann_pct     REAL,
    max_drawdown_pct    REAL,
    aum_crore           INTEGER,
    expense_ratio_pct   REAL,
    morningstar_rating  INTEGER,
    risk_grade          TEXT,
    is_high_alpha       INTEGER,
    is_low_expense      INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

-- 6. Fact: Fund House AUM Trends
DROP TABLE IF EXISTS fact_aum;
CREATE TABLE fact_aum (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    date                TEXT NOT NULL,
    fund_house          TEXT NOT NULL,
    aum_lakh_crore      REAL NOT NULL,
    aum_crore           INTEGER NOT NULL,
    num_schemes         INTEGER NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date (date)
);

-- 7. Fact: Portfolio Stock Holdings
DROP TABLE IF EXISTS fact_portfolio_holdings;
CREATE TABLE fact_portfolio_holdings (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code           INTEGER NOT NULL,
    stock_symbol        TEXT NOT NULL,
    stock_name          TEXT NOT NULL,
    sector              TEXT NOT NULL,
    weight_pct          REAL NOT NULL,
    market_value_cr     REAL NOT NULL,
    current_price_inr   REAL NOT NULL,
    portfolio_date      TEXT NOT NULL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund (amfi_code)
);

-- 8. Fact: Monthly Category Inflows
DROP TABLE IF EXISTS fact_category_inflows;
CREATE TABLE fact_category_inflows (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    month               TEXT NOT NULL, -- YYYY-MM
    category            TEXT NOT NULL,
    net_inflow_crore    REAL NOT NULL
);

-- 9. Fact: Monthly SIP Inflows
DROP TABLE IF EXISTS fact_sip_inflows;
CREATE TABLE fact_sip_inflows (
    month                      TEXT PRIMARY KEY, -- YYYY-MM
    sip_inflow_crore           INTEGER NOT NULL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh     REAL,
    sip_aum_lakh_crore        REAL,
    yoy_growth_pct            REAL
);

-- 10. Fact: Benchmark Indices History
DROP TABLE IF EXISTS fact_benchmark_indices;
CREATE TABLE fact_benchmark_indices (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    date                TEXT NOT NULL,
    index_name          TEXT NOT NULL,
    close_value         REAL NOT NULL,
    FOREIGN KEY (date) REFERENCES dim_date (date)
);

-- 11. Fact: Industry Folio Count
DROP TABLE IF EXISTS fact_industry_folio_count;
CREATE TABLE fact_industry_folio_count (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    month                   TEXT NOT NULL, -- YYYY-MM
    total_folios_crore      REAL NOT NULL,
    equity_folios_crore     REAL NOT NULL,
    debt_folios_crore       REAL NOT NULL,
    hybrid_folios_crore     REAL NOT NULL,
    others_folios_crore     REAL NOT NULL
);

-- ============================================================================
-- INDEXES FOR QUERY OPTIMIZATION
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav (amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi_date ON fact_transactions (amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_tx_investor ON fact_transactions (investor_id);
CREATE INDEX IF NOT EXISTS idx_holdings_amfi ON fact_portfolio_holdings (amfi_code);
CREATE INDEX IF NOT EXISTS idx_aum_fh_date ON fact_aum (fund_house, date);
