#!/usr/bin/env python3
"""
Task 2: REST API & JSON Data Extraction Script
Calls public financial APIs (mfapi.in REST endpoint), inspects JSON responses,
parses nested payloads, and exports structured records into CSV for downstream analytics.
"""

import os
import sys
import requests
import pandas as pd

# Directories
PROCESSED_DIR = os.path.join("data", "processed")
os.makedirs(PROCESSED_DIR, exist_ok=True)

def fetch_api_data(amfi_code=119551):
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    print(f"Calling REST API: {url} ...")
    
    headers = {"User-Agent": "Bluestock-Analytics-Client/1.0"}
    response = requests.get(url, headers=headers, timeout=15)
    
    if response.status_code != 200:
        print(f"Error: API returned status code {response.status_code}")
        sys.exit(1)
        
    json_data = response.json()
    print("API Response Received. Inspecting JSON Structure...")
    print(f"Keys in JSON: {list(json_data.keys())}")
    
    meta = json_data.get("meta", {})
    print(f"Meta Info: Scheme Name = '{meta.get('scheme_name')}', Fund House = '{meta.get('fund_house')}'")
    
    raw_nav_list = json_data.get("data", [])
    print(f"Total NAV Time-Series Records Received: {len(raw_nav_list)}")
    
    # Parse JSON list of dicts into Pandas DataFrame
    df = pd.DataFrame(raw_nav_list)
    df["amfi_code"] = amfi_code
    df["scheme_name"] = meta.get("scheme_name")
    df["scheme_category"] = meta.get("scheme_category")
    df["scheme_type"] = meta.get("scheme_type")
    df["fund_house"] = meta.get("fund_house")
    
    # Convert NAV to float and Date to datetime
    df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
    df = df.sort_values("date").reset_index(drop=True)
    
    # Calculate daily percentage return
    df["daily_return_pct"] = df["nav"].pct_change() * 100.0
    
    out_csv = os.path.join(PROCESSED_DIR, "api_extracted_data.csv")
    df.to_csv(out_csv, index=False)
    print(f"Successfully extracted API JSON data into CSV: '{out_csv}' (Shape: {df.shape})")
    
    return df

if __name__ == "__main__":
    fetch_api_data()
