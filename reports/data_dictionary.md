# BlueStock Mutual Fund Platform - Data Dictionary

This document details the database schema, table definitions, column attributes, data types, primary/foreign keys, business rules, and source file mappings for the `bluestock_mf.db` SQLite database.

---

## 1. Overview & Architecture

The database is designed using a **Star Schema** architecture optimized for financial analytics, NAV time-series tracking, portfolio holdings inspection, and investor transaction behavior modeling.

```
                  +-------------------+
                  |     dim_fund      |
                  +-------------------+
                  | amfi_code (PK)    |
                  +---------+---------+
                            |
           +----------------+----------------+
           |                |                |
+----------v--------+ +-----v-----------+ +--v----------------+
|     fact_nav      | |fact_transactions| | fact_performance  |
+-------------------+ +-----------------+ +-------------------+
| id (PK)           | | transaction_id  | | amfi_code (PK,FK) |
| amfi_code (FK)    | | amfi_code (FK)  | +-------------------+
| date (FK)         | | date (FK)       |
+---------+---------+ +-----+-----------+
          |                 |
          +--------+--------+
                   |
         +---------v---------+
         |     dim_date      |
         +-------------------+
         | date (PK)         |
         +-------------------+
```

---

## 2. Table Specifications

### 2.1 `dim_fund` (Dimension: Fund Master)
- **Source File**: `data/processed/01_fund_master.csv`
- **Description**: Master catalog of mutual fund schemes, fund management metadata, and expense structures.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Unique 6-digit identifier assigned by AMFI. |
| `scheme_name` | TEXT | NOT NULL | Official name of the mutual fund scheme option. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) managing the fund. |
| `category` | TEXT | NOT NULL | Broad asset class category (`Equity` or `Debt`). |
| `sub_category` | TEXT | NOT NULL | SEBI sub-category classification (e.g., `Large Cap`, `Small Cap`, `Gilt`). |
| `plan` | TEXT | NOT NULL | Plan distribution type (`Regular` vs `Direct`). |
| `launch_date` | TEXT | YYYY-MM-DD | Inception date of the scheme option. |
| `benchmark` | TEXT | NULLABLE | Primary benchmark index against which performance is measured. |
| `expense_ratio_pct` | REAL | CHECK (0.1 - 2.5) | Annual operating expense ratio percentage charged by the AMC. |
| `exit_load_pct` | REAL | NULLABLE | Exit load percentage levied on early redemptions. |
| `min_sip_amount` | INTEGER | NULLABLE | Minimum monthly Systematic Investment Plan (SIP) amount in INR. |
| `min_lumpsum_amount` | INTEGER | NULLABLE | Minimum initial one-time lumpsum investment amount in INR. |
| `fund_manager` | TEXT | NULLABLE | Name of the primary fund portfolio manager. |
| `risk_category` | TEXT | NULLABLE | SEBI Riskometer classification (`Low`, `Moderate`, `Very High`, etc.). |
| `sebi_category_code` | TEXT | NULLABLE | Standardized SEBI categorization code (e.g., `EC01`, `DC02`). |

---

### 2.2 `dim_date` (Dimension: Calendar Master)
- **Source File**: Dynamically generated calendar dimension across all historical date boundaries.
- **Description**: Standardized date dimension supporting time-series aggregation by day, month, quarter, and year.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | PRIMARY KEY (YYYY-MM-DD) | Calendar date string identifier. |
| `year` | INTEGER | NOT NULL | 4-digit calendar year (e.g., `2024`). |
| `quarter` | INTEGER | CHECK (1-4) | Calendar quarter (`1`, `2`, `3`, `4`). |
| `month` | INTEGER | CHECK (1-12) | Numeric month (`1` to `12`). |
| `month_name` | TEXT | NOT NULL | Full month name (e.g., `January`, `March`). |
| `day` | INTEGER | CHECK (1-31) | Day of the month (`1` to `31`). |
| `day_of_week` | INTEGER | CHECK (0-6) | Day index where `0` = Monday and `6` = Sunday. |
| `is_weekend` | INTEGER | CHECK (0, 1) | Binary flag (`1` for Saturday/Sunday, `0` for weekdays). |

---

### 2.3 `fact_nav` (Fact: Daily Net Asset Value)
- **Source File**: `data/processed/02_nav_history.csv`
- **Description**: Historical daily Net Asset Value (NAV) price records per fund scheme. Includes continuous calendar dates (weekends/holidays forward-filled).

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate primary key. |
| `amfi_code` | INTEGER | FOREIGN KEY -> `dim_fund` | AMFI scheme identifier. |
| `date` | TEXT | FOREIGN KEY -> `dim_date` | Date of NAV publication (YYYY-MM-DD). |
| `nav` | REAL | CHECK (nav > 0) | Net Asset Value price per unit in INR. |

---

### 2.4 `fact_transactions` (Fact: Investor Transactions)
- **Source File**: `data/processed/08_investor_transactions.csv`
- **Description**: Granular investor buy/sell activity logs including demographic metadata and transaction channels.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `transaction_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique transaction sequence identifier. |
| `investor_id` | TEXT | NOT NULL | Masked investor account identifier (e.g., `INV003054`). |
| `transaction_date` | TEXT | FOREIGN KEY -> `dim_date` | Execution date of the transaction (YYYY-MM-DD). |
| `amfi_code` | INTEGER | FOREIGN KEY -> `dim_fund` | Target scheme code invested or redeemed. |
| `transaction_type` | TEXT | ENUM (`SIP`, `Lumpsum`, `Redemption`) | Type of investor transaction. |
| `amount_inr` | INTEGER | CHECK (amount > 0) | Gross transaction value in INR (stored as positive integer). |
| `net_amount_inr` | INTEGER | SIGNED | Computed net cash flow in INR (Negative for `Redemption`, Positive for `SIP`/`Lumpsum`). |
| `state` | TEXT | NULLABLE | Investor state location in India. |
| `city` | TEXT | NULLABLE | Investor city location. |
| `city_tier` | TEXT | NULLABLE | City tier classification (`Tier 1`, `Tier 2`, `Tier 3`). |
| `age_group` | TEXT | NULLABLE | Investor demographic age range (e.g., `26-35`, `36-50`). |
| `gender` | TEXT | NULLABLE | Gender classification. |
| `annual_income_lakh` | REAL | NULLABLE | Investor annual income in INR Lakhs. |
| `payment_mode` | TEXT | NULLABLE | Payment execution channel (`UPI`, `Net Banking`, `Mandate`, `Cheque`). |
| `kyc_status` | TEXT | NULLABLE | Compliance KYC status (`Verified`, `Pending`, `Rejected`). |

---

### 2.5 `fact_performance` (Fact: Scheme Performance & Risk Metrics)
- **Source File**: `data/processed/07_scheme_performance.csv`
- **Description**: Historical returns, volatility statistics, risk-adjusted ratios, and fund ratings.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK -> `dim_fund` | AMFI scheme identifier. |
| `scheme_name` | TEXT | NOT NULL | Scheme name option. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company name. |
| `category` | TEXT | NOT NULL | Broad asset class category. |
| `plan` | TEXT | NOT NULL | Distribution plan variant (`Regular`/`Direct`). |
| `return_1yr_pct` | REAL | NULLABLE | 1-Year annualized return percentage. |
| `return_3yr_pct` | REAL | NULLABLE | 3-Year CAGR return percentage. |
| `return_5yr_pct` | REAL | NULLABLE | 5-Year CAGR return percentage. |
| `benchmark_3yr_pct` | REAL | NULLABLE | Benchmark 3-Year CAGR return percentage. |
| `alpha` | REAL | NULLABLE | Jensen's Alpha (Outperformance vs risk-adjusted benchmark). |
| `beta` | REAL | NULLABLE | Beta coefficient (Systematic market volatility sensitivity). |
| `sharpe_ratio` | REAL | NULLABLE | Sharpe Ratio (Risk-adjusted return above risk-free rate). |
| `sortino_ratio` | REAL | NULLABLE | Sortino Ratio (Risk-adjusted return considering downside risk). |
| `std_dev_ann_pct` | REAL | NULLABLE | Annualized standard deviation (Volatiliy %). |
| `max_drawdown_pct` | REAL | NULLABLE | Maximum peak-to-trough value decline %. |
| `aum_crore` | INTEGER | NULLABLE | Scheme AUM size in INR Crores. |
| `expense_ratio_pct` | REAL | CHECK (0.1 - 2.5) | Operating expense ratio %. |
| `morningstar_rating` | INTEGER | CHECK (1 - 5) | Morningstar star rating (1 to 5 stars). |
| `risk_grade` | TEXT | NULLABLE | Risk grade classification (`Low`, `Moderate`, `Very High`). |
| `is_high_alpha` | INTEGER | CHECK (0, 1) | Flag indicating Alpha > 3.0. |
| `is_low_expense` | INTEGER | CHECK (0, 1) | Flag indicating Expense Ratio < 1.0%. |

---

### 2.6 `fact_aum` (Fact: Fund House AUM Trends)
- **Source File**: `data/processed/03_aum_by_fund_house.csv`
- **Description**: Quarterly Asset Under Management trends per AMC.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate primary key. |
| `date` | TEXT | FOREIGN KEY -> `dim_date` | Quarter-end reporting date (YYYY-MM-DD). |
| `fund_house` | TEXT | NOT NULL | Asset Management Company name. |
| `aum_lakh_crore` | REAL | NOT NULL | Total AUM in INR Lakh Crores. |
| `aum_crore` | INTEGER | NOT NULL | Total AUM in INR Crores. |
| `num_schemes` | INTEGER | NOT NULL | Total count of active schemes offered by AMC. |

---

### 2.7 `fact_portfolio_holdings` (Fact: Stock Portfolio Holdings)
- **Source File**: `data/processed/09_portfolio_holdings.csv`
- **Description**: Underlying equity stock breakdown and sector allocation per fund scheme.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate primary key. |
| `amfi_code` | INTEGER | FOREIGN KEY -> `dim_fund` | AMFI scheme identifier holding the stock. |
| `stock_symbol` | TEXT | NOT NULL | NSE/BSE ticker symbol (e.g., `HDFCBANK`). |
| `stock_name` | TEXT | NOT NULL | Company name of equity security. |
| `sector` | TEXT | NOT NULL | Economy sector classification (e.g., `Financial Services`, `IT`). |
| `weight_pct` | REAL | NOT NULL | Portfolio weight percentage allocation. |
| `market_value_cr` | REAL | NOT NULL | Position market value in INR Crores. |
| `current_price_inr` | REAL | NOT NULL | Market closing stock price in INR. |
| `portfolio_date` | TEXT | YYYY-MM-DD | Date of portfolio disclosure. |

---

### 2.8 `fact_category_inflows` (Fact: Monthly Category Net Inflows)
- **Source File**: `data/processed/05_category_inflows.csv`
- **Description**: Monthly industry net inflow trends across scheme categories.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate primary key. |
| `month` | TEXT | YYYY-MM | Reporting month. |
| `category` | TEXT | NOT NULL | Category name (`Large Cap`, `Small Cap`, etc.). |
| `net_inflow_crore` | REAL | NOT NULL | Net capital inflow in INR Crores. |

---

### 2.9 `fact_sip_inflows` (Fact: Industry Monthly SIP Trends)
- **Source File**: `data/processed/04_monthly_sip_inflows.csv`
- **Description**: Industry aggregate SIP inflow metrics, active account counts, and YoY growth.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY (YYYY-MM) | Reporting month string identifier. |
| `sip_inflow_crore` | INTEGER | NOT NULL | Total SIP gross collections in INR Crores. |
| `active_sip_accounts_crore` | REAL | NULLABLE | Total active SIP accounts count in Crores. |
| `new_sip_accounts_lakh` | REAL | NULLABLE | New SIP accounts registered during month in Lakhs. |
| `sip_aum_lakh_crore` | REAL | NULLABLE | Cumulative SIP AUM in INR Lakh Crores. |
| `yoy_growth_pct` | REAL | NULLABLE | Year-over-Year growth percentage in SIP inflows. |

---

### 2.10 `fact_benchmark_indices` (Fact: Benchmark Indices History)
- **Source File**: `data/processed/10_benchmark_indices.csv`
- **Description**: Daily closing values for major Indian market benchmark indices.

| Column Name | Data Type | Key / Constraints | Business Definition |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Surrogate primary key. |
| `date` | TEXT | FOREIGN KEY -> `dim_date` | Price quotation date (YYYY-MM-DD). |
| `index_name` | TEXT | NOT NULL | Benchmark name (`NIFTY50`, `NIFTY_MIDCAP150`, etc.). |
| `close_value` | REAL | NOT NULL | Market closing index point value. |
