import os
import time
import requests
import pandas as pd

RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

def fetch_single_scheme(scheme_code, retries=3):
    """Fetch NAV records and metadata for a single scheme code."""
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    print(f"Fetching from: {url} ...")
    
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            payload = response.json()
            meta = payload.get("meta", {})
            nav_data = payload.get("data", [])
            
            df = pd.DataFrame(nav_data)
            if not df.empty:
                df["amfi_code"] = scheme_code
                df["scheme_name"] = meta.get("scheme_name", "")
                df["fund_house"] = meta.get("fund_house", "")
                df["scheme_type"] = meta.get("scheme_type", "")
                df["scheme_category"] = meta.get("scheme_category", "")
                cols = ["amfi_code", "scheme_name", "fund_house", "scheme_type", "scheme_category", "date", "nav"]
                df = df[cols]
            return df, meta
        except Exception as e:
            print(f"Attempt {attempt}/{retries} failed for {scheme_code}: {e}")
            if attempt == retries:
                raise e
            time.sleep(2)

def main():
    # 1. Fetch HDFC Top 100 Direct (Scheme Code: 125497)
    df_125497, meta_125497 = fetch_single_scheme(125497)
    path_raw_125497 = os.path.join(RAW_DIR, "live_nav_125497.csv")
    df_125497.to_csv(path_raw_125497, index=False)
    print(f"Saved {len(df_125497)} records for 125497 to {path_raw_125497}")

    # 2. Fetch 5 key schemes:
    # 119551 (SBI Bluechip), 120503 (ICICI Bluechip), 118632 (Nippon Large Cap), 119092 (Axis Bluechip), 120841 (Kotak Bluechip)
    key_codes = [119551, 120503, 118632, 119092, 120841]
    dfs = []
    
    for code in key_codes:
        try:
            df, meta = fetch_single_scheme(code)
            dfs.append(df)
            
            indiv_raw = os.path.join(RAW_DIR, f"live_nav_{code}.csv")
            df.to_csv(indiv_raw, index=False)
            print(f"Fetched scheme {code} ('{meta.get('scheme_name')}'): {len(df)} rows -> Saved to {indiv_raw}")
        except Exception as e:
            print(f"Error fetching scheme {code}: {e}")
            
    if dfs:
        df_combined = pd.concat(dfs, ignore_index=True)
        path_raw_5 = os.path.join(RAW_DIR, "live_nav_5_key_schemes.csv")
        df_combined.to_csv(path_raw_5, index=False)
        print(f"Saved total {len(df_combined)} records across 5 key schemes to {path_raw_5}")

if __name__ == "__main__":
    main()
