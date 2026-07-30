import os
import pandas as pd
import numpy as np

RAW_DIR = "csv"
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def find_file(file_name):
    possible_paths = [
        os.path.join(RAW_DIR, file_name),
        file_name,
        os.path.join("data", "raw", file_name)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return file_name

def clean_nav_history():
    file_path = find_file("02_nav_history.csv")
    print(f"Cleaning nav_history from {file_path} ...")
    df = pd.read_csv(file_path)
    
    # Parse dates
    df["date"] = pd.to_datetime(df["date"])
    
    # Remove duplicates
    df = df.drop_duplicates(subset=["amfi_code", "date"])
    
    # Sort
    df = df.sort_values(by=["amfi_code", "date"]).reset_index(drop=True)
    
    # Validate nav > 0
    assert (df["nav"] > 0).all(), "Invalid NAV values <= 0 found!"
    
    # Forward fill missing dates (weekends/holidays) per amfi_code
    cleaned_dfs = []
    for amfi_code, group in df.groupby("amfi_code"):
        group = group.set_index("date")
        min_date = group.index.min()
        max_date = group.index.max()
        
        full_date_range = pd.date_range(start=min_date, end=max_date, freq="D", name="date")
        reindexed_group = group.reindex(full_date_range)
        
        reindexed_group["amfi_code"] = amfi_code
        reindexed_group["nav"] = reindexed_group["nav"].ffill().bfill()
        
        reindexed_group = reindexed_group.reset_index()
        cleaned_dfs.append(reindexed_group)
        
    cleaned_df = pd.concat(cleaned_dfs, ignore_index=True)
    cleaned_df["date"] = cleaned_df["date"].dt.strftime("%Y-%m-%d")
    
    out_path = os.path.join(PROCESSED_DIR, "02_nav_history.csv")
    cleaned_df.to_csv(out_path, index=False)
    print(f"Cleaned nav_history saved to {out_path} | Shape: {cleaned_df.shape}")
    return cleaned_df

def clean_investor_transactions():
    file_path = find_file("08_investor_transactions.csv")
    print(f"\nCleaning investor_transactions from {file_path} ...")
    df = pd.read_csv(file_path)
    
    # Standardize transaction_type
    df["transaction_type"] = df["transaction_type"].str.strip().str.capitalize()
    df["transaction_type"] = df["transaction_type"].replace({"Sip": "SIP", "Lumpsum": "Lumpsum", "Redemption": "Redemption"})
    valid_types = {"SIP", "Lumpsum", "Redemption"}
    assert set(df["transaction_type"].unique()).issubset(valid_types), "Unexpected transaction types found!"
    
    # Validate amount_inr > 0
    assert (df["amount_inr"] > 0).all(), "Invalid negative/zero transaction amounts found!"
    
    # Fix date formats
    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.strftime("%Y-%m-%d")
    
    # Check KYC status enum
    df["kyc_status"] = df["kyc_status"].str.strip().str.title()
    
    # Sort
    df = df.sort_values(by=["transaction_date", "investor_id"]).reset_index(drop=True)
    
    out_path = os.path.join(PROCESSED_DIR, "08_investor_transactions.csv")
    df.to_csv(out_path, index=False)
    print(f"Cleaned investor_transactions saved to {out_path} | Shape: {df.shape}")
    return df

def clean_scheme_performance():
    file_path = find_file("07_scheme_performance.csv")
    print(f"\nCleaning scheme_performance from {file_path} ...")
    df = pd.read_csv(file_path)
    
    # Validate numeric returns
    return_cols = ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct", "max_drawdown_pct"]
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        
    # Check expense_ratio_pct range (0.1% - 2.5%)
    min_exp, max_exp = df["expense_ratio_pct"].min(), df["expense_ratio_pct"].max()
    print(f"Expense Ratio Range: {min_exp:.2f}% to {max_exp:.2f}%")
    assert 0.1 <= min_exp and max_exp <= 2.5, f"Expense ratio out of expected range! ({min_exp}, {max_exp})"
    
    # Flag anomalies
    df["is_high_alpha"] = df["alpha"] > 3.0
    df["is_low_expense"] = df["expense_ratio_pct"] < 1.0
    
    out_path = os.path.join(PROCESSED_DIR, "07_scheme_performance.csv")
    df.to_csv(out_path, index=False)
    print(f"Cleaned scheme_performance saved to {out_path} | Shape: {df.shape}")
    return df

def clean_other_datasets():
    other_files = [
        ("01_fund_master.csv", ["launch_date"]),
        ("03_aum_by_fund_house.csv", ["date"]),
        ("04_monthly_sip_inflows.csv", []),
        ("05_category_inflows.csv", []),
        ("06_industry_folio_count.csv", []),
        ("09_portfolio_holdings.csv", ["portfolio_date"]),
        ("10_benchmark_indices.csv", ["date"])
    ]
    
    for filename, date_cols in other_files:
        file_path = find_file(filename)
        print(f"Processing {filename} from {file_path} ...")
        df = pd.read_csv(file_path)
        
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime("%Y-%m-%d")
                
        df = df.drop_duplicates().reset_index(drop=True)
        out_path = os.path.join(PROCESSED_DIR, filename)
        df.to_csv(out_path, index=False)
        print(f"Saved {filename} to {out_path} | Shape: {df.shape}")

def main():
    print("=" * 80)
    print("STARTING DATA CLEANING PIPELINE")
    print("=" * 80)
    
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    clean_other_datasets()
    
    print("\nData cleaning pipeline completed successfully. All 10 cleaned CSVs saved in data/processed/")

if __name__ == "__main__":
    main()
