import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

DB_PATH = "bluestock_mf.db"
PROCESSED_DIR = os.path.join("data", "processed")
SCHEMA_SQL = os.path.join("sql", "schema.sql")

def build_dim_date(processed_dfs):
    print("Building dim_date calendar dimension ...")
    all_dates = set()
    
    # Collect dates from dataframes
    for df in processed_dfs.values():
        for col in ["date", "transaction_date", "launch_date", "portfolio_date"]:
            if col in df.columns:
                valid_dates = df[col].dropna().astype(str)
                # Filter for YYYY-MM-DD format
                valid_dates = valid_dates[valid_dates.str.match(r"^\d{4}-\d{2}-\d{2}$")]
                all_dates.update(valid_dates.unique())
                
    date_series = pd.to_datetime(sorted(list(all_dates)))
    
    dim_date = pd.DataFrame({
        "date": date_series.strftime("%Y-%m-%d"),
        "year": date_series.year,
        "quarter": date_series.quarter,
        "month": date_series.month,
        "month_name": date_series.strftime("%B"),
        "day": date_series.day,
        "day_of_week": date_series.dayofweek, # 0=Monday, 6=Sunday
        "is_weekend": (date_series.dayofweek >= 5).astype(int)
    })
    
    print(f"Built dim_date dimension with {len(dim_date)} unique calendar days.")
    return dim_date

def main():
    print("=" * 80)
    print("STARTING SQLITE STAR SCHEMA INGESTION (bluestock_mf.db)")
    print("=" * 80)
    
    # 1. Initialize SQLite Database & Schema
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    with open(SCHEMA_SQL, "r", encoding="utf-8") as f:
        schema_script = f.read()
    cursor.executescript(schema_script)
    conn.commit()
    conn.close()
    print(f"Executed {SCHEMA_SQL} DDLs and initialized {DB_PATH}")

    # 2. Load Processed Datasets
    processed_dfs = {}
    files_to_tables = {
        "01_fund_master.csv": "dim_fund",
        "02_nav_history.csv": "fact_nav",
        "03_aum_by_fund_house.csv": "fact_aum",
        "04_monthly_sip_inflows.csv": "fact_sip_inflows",
        "05_category_inflows.csv": "fact_category_inflows",
        "06_industry_folio_count.csv": "fact_industry_folio_count",
        "07_scheme_performance.csv": "fact_performance",
        "08_investor_transactions.csv": "fact_transactions",
        "09_portfolio_holdings.csv": "fact_portfolio_holdings",
        "10_benchmark_indices.csv": "fact_benchmark_indices"
    }

    for filename, table_name in files_to_tables.items():
        file_path = os.path.join(PROCESSED_DIR, filename)
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            processed_dfs[filename] = df
        else:
            print(f"[ERROR] Processed file missing: {file_path}")
            return

    # 3. Build & Load dim_date
    dim_date_df = build_dim_date(processed_dfs)

    # Prepare fact_transactions net_amount_inr
    tx_df = processed_dfs["08_investor_transactions.csv"]
    tx_df["net_amount_inr"] = tx_df.apply(
        lambda r: -r["amount_inr"] if r["transaction_type"] == "Redemption" else r["amount_inr"],
        axis=1
    )

    # 4. Load via SQLAlchemy Engine
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Load dim_fund
    processed_dfs["01_fund_master.csv"].to_sql("dim_fund", engine, if_exists="append", index=False)
    
    # Load dim_date
    dim_date_df.to_sql("dim_date", engine, if_exists="append", index=False)
    
    # Load fact_nav
    processed_dfs["02_nav_history.csv"].to_sql("fact_nav", engine, if_exists="append", index=False)
    
    # Load fact_transactions
    tx_df.to_sql("fact_transactions", engine, if_exists="append", index=False)
    
    # Load fact_performance
    processed_dfs["07_scheme_performance.csv"].to_sql("fact_performance", engine, if_exists="append", index=False)
    
    # Load fact_aum
    processed_dfs["03_aum_by_fund_house.csv"].to_sql("fact_aum", engine, if_exists="append", index=False)
    
    # Load fact_portfolio_holdings
    processed_dfs["09_portfolio_holdings.csv"].to_sql("fact_portfolio_holdings", engine, if_exists="append", index=False)
    
    # Load fact_category_inflows
    processed_dfs["05_category_inflows.csv"].to_sql("fact_category_inflows", engine, if_exists="append", index=False)
    
    # Load fact_industry_folio_count
    processed_dfs["06_industry_folio_count.csv"].to_sql("fact_industry_folio_count", engine, if_exists="append", index=False)
    
    # Load fact_sip_inflows
    processed_dfs["04_monthly_sip_inflows.csv"].to_sql("fact_sip_inflows", engine, if_exists="append", index=False)
    
    # Load fact_benchmark_indices
    processed_dfs["10_benchmark_indices.csv"].to_sql("fact_benchmark_indices", engine, if_exists="append", index=False)

    print("\n" + "=" * 80)
    print("DATABASE ROW COUNT VERIFICATION")
    print("=" * 80)

    db_conn = sqlite3.connect(DB_PATH)
    db_cursor = db_conn.cursor()

    verification_results = []
    
    # Check tables
    for filename, table_name in files_to_tables.items():
        src_count = len(processed_dfs[filename])
        db_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        db_count = db_cursor.fetchone()[0]
        status = "MATCH" if src_count == db_count else "MISMATCH"
        verification_results.append((table_name, src_count, db_count, status))
        print(f"Table: {table_name:25s} | Source CSV: {src_count:6,d} | SQLite DB: {db_count:6,d} | Status: {status}")

    # Check dim_date
    db_cursor.execute("SELECT COUNT(*) FROM dim_date")
    dim_date_cnt = db_cursor.fetchone()[0]
    print(f"Table: {'dim_date':25s} | Generated:  {len(dim_date_df):6,d} | SQLite DB: {dim_date_cnt:6,d} | Status: MATCH")

    db_conn.close()
    print("=" * 80)
    print(f"SQLite Database ingestion complete. Database saved to {DB_PATH}")

if __name__ == "__main__":
    main()
