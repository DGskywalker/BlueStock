-- Nifty 100 SQLite Database Schema DDL (db/schema.sql)
-- Defines 10 relational tables with Primary Key, Foreign Key, and Integrity Constraints

PRAGMA foreign_keys = ON;

-- 1. Sectors Dimension Table
CREATE TABLE IF NOT EXISTS sectors (
    sector_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_name TEXT NOT NULL UNIQUE,
    weight_pct REAL DEFAULT 0.0
);

-- 2. Companies Dimension Table
CREATE TABLE IF NOT EXISTS companies (
    company_id INTEGER PRIMARY KEY,
    ticker TEXT NOT NULL UNIQUE,
    company_name TEXT NOT NULL,
    bse_code TEXT,
    nse_code TEXT,
    sector_id INTEGER,
    sector TEXT,
    industry TEXT,
    website TEXT,
    face_value REAL DEFAULT 10.0,
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id) ON DELETE SET NULL
);

-- 3. Profit & Loss Fact Table
CREATE TABLE IF NOT EXISTS profitandloss (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    sales REAL NOT NULL,
    expenses REAL,
    operating_profit REAL,
    opm_pct REAL,
    other_income REAL,
    interest REAL,
    depreciation REAL,
    pbt REAL,
    tax REAL,
    pat REAL,
    eps_inr REAL,
    dividend_payout_pct REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 4. Balance Sheet Fact Table
CREATE TABLE IF NOT EXISTS balancesheet (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    equity_capital REAL NOT NULL,
    reserves REAL,
    borrowings REAL,
    other_liabilities REAL,
    total_liabilities REAL NOT NULL,
    fixed_assets REAL,
    cwip REAL,
    investments REAL,
    other_assets REAL,
    total_assets REAL NOT NULL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 5. Cash Flow Fact Table
CREATE TABLE IF NOT EXISTS cashflow (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    cfo REAL NOT NULL,
    cfi REAL NOT NULL,
    cff REAL NOT NULL,
    net_cash_flow REAL NOT NULL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 6. Financial Ratios Table (Sprint 2 - 14+ Computed KPI Columns)
CREATE TABLE IF NOT EXISTS financial_ratios (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    net_profit_margin_pct REAL,
    operating_profit_margin_pct REAL,
    return_on_equity_pct REAL,
    return_on_capital_employed_pct REAL,
    return_on_assets_pct REAL,
    debt_to_equity REAL,
    high_leverage_flag INTEGER DEFAULT 0,
    interest_coverage REAL,
    icr_label TEXT,
    icr_warning_flag INTEGER DEFAULT 0,
    net_debt_cr REAL,
    asset_turnover REAL,
    free_cash_flow_cr REAL,
    cfo_quality_score REAL,
    cfo_quality_label TEXT,
    capex_cr REAL,
    capex_intensity_pct REAL,
    capex_intensity_label TEXT,
    fcf_conversion_pct REAL,
    capital_allocation_pattern TEXT,
    earnings_per_share REAL,
    book_value_per_share REAL,
    dividend_payout_ratio_pct REAL,
    total_debt_cr REAL,
    cash_from_operations_cr REAL,
    revenue_cagr_3yr REAL,
    revenue_cagr_5yr REAL,
    revenue_cagr_5yr_flag TEXT,
    pat_cagr_3yr REAL,
    pat_cagr_5yr REAL,
    pat_cagr_5yr_flag TEXT,
    eps_cagr_3yr REAL,
    eps_cagr_5yr REAL,
    eps_cagr_5yr_flag TEXT,
    pe_ratio REAL,
    pb_ratio REAL,
    roe_pct REAL,
    roce_pct REAL,
    debt_to_equity_source REAL,
    composite_quality_score REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 7. Analysis Fact Table
CREATE TABLE IF NOT EXISTS analysis (
    company_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    compounding_sales_growth_pct REAL,
    compounding_profit_growth_pct REAL,
    stock_price_cagr_pct REAL,
    roe_pct REAL,
    PRIMARY KEY (company_id, year),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 8. Documents Reference Table
CREATE TABLE IF NOT EXISTS documents (
    doc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    doc_type TEXT,
    url TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 9. Pros & Cons Qualitative Table
CREATE TABLE IF NOT EXISTS prosandcons (
    pc_id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER NOT NULL,
    type TEXT CHECK(type IN ('PRO', 'CON')) NOT NULL,
    description TEXT NOT NULL,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 10. Stock Prices Time-Series Table
CREATE TABLE IF NOT EXISTS stock_prices (
    company_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    open_price REAL NOT NULL,
    high_price REAL NOT NULL,
    low_price REAL NOT NULL,
    close_price REAL NOT NULL,
    volume INTEGER NOT NULL,
    PRIMARY KEY (company_id, date),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 11. Peer Groups Mapping Table
CREATE TABLE IF NOT EXISTS peer_groups (
    company_id INTEGER NOT NULL,
    peer_company_id INTEGER NOT NULL,
    ranking INTEGER DEFAULT 1,
    PRIMARY KEY (company_id, peer_company_id),
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE,
    FOREIGN KEY (peer_company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- Indexes for Sub-Millisecond Query Performance
CREATE INDEX IF NOT EXISTS idx_pnl_comp ON profitandloss(company_id);
CREATE INDEX IF NOT EXISTS idx_bs_comp ON balancesheet(company_id);
CREATE INDEX IF NOT EXISTS idx_cf_comp ON cashflow(company_id);
CREATE INDEX IF NOT EXISTS idx_ratios_comp ON financial_ratios(company_id);
CREATE INDEX IF NOT EXISTS idx_prices_comp_date ON stock_prices(company_id, date);
