#!/usr/bin/env python3
"""
Bonus Challenge B1: Weekday 8 PM Cron Scheduler
Auto-fetches live NAV from mfapi.in API every weekday (Monday-Friday) at 8:00 PM (20:00).
"""

import os
import sys
import time
import datetime
import requests
import pandas as pd

# Setup Directories
SCRIPTS_DIR = "scripts"
RAW_DIR = os.path.join("data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# 5 Key Benchmark Schemes
SCHEMES = {
    119551: "SBI Bluechip Fund",
    120503: "ICICI Pru Multi Asset Fund",
    118632: "HDFC Small Cap Fund",
    119092: "Axis Long Term Equity Fund",
    120841: "Kotak Emerging Equity Fund"
}

def fetch_live_nav_job():
    now = datetime.datetime.now()
    # Check if weekday (Monday=0 ... Friday=4, Saturday=5, Sunday=6)
    if now.weekday() >= 5:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Weekend detected. Skipping live NAV fetch.")
        return

    print(f"\n================================================================================")
    print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] RUNNING WEEKDAY 8 PM LIVE NAV FETCH JOB")
    print(f"================================================================================")

    records = []
    for code, name in SCHEMES.items():
        url = f"https://api.mfapi.in/mf/{code}"
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                meta = data.get("meta", {})
                nav_list = data.get("data", [])
                if nav_list:
                    latest = nav_list[0]
                    records.append({
                        "amfi_code": code,
                        "scheme_name": meta.get("scheme_name", name),
                        "fund_house": meta.get("fund_house", "Unknown"),
                        "nav_date": latest.get("date"),
                        "live_nav": float(latest.get("nav")),
                        "fetch_timestamp": now.strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"  [SUCCESS] Code: {code} | {name[:25]} | Date: {latest.get('date')} | NAV: ₹{latest.get('nav')}")
        except Exception as e:
            print(f"  [ERROR] Code {code}: {e}")

    if records:
        df = pd.DataFrame(records)
        out_path = os.path.join(RAW_DIR, f"live_nav_{now.strftime('%Y%m%d')}.csv")
        df.to_csv(out_path, index=False)
        print(f"Saved live NAV records to {out_path}")
    print("================================================================================\n")

def start_scheduler(run_immediately=True):
    print("Starting Weekday 8:00 PM Cron Scheduler Daemon for live NAV fetch...")
    if run_immediately:
        fetch_live_nav_job()

    print("Scheduler running in background. Waiting for weekday 20:00 trigger...")
    try:
        while True:
            now = datetime.datetime.now()
            # Trigger if hour == 20 and minute == 0
            if now.hour == 20 and now.minute == 0 and now.weekday() < 5:
                fetch_live_nav_job()
                time.sleep(60) # Sleep 60s to prevent multiple triggers in same minute
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nScheduler stopped by user.")

if __name__ == "__main__":
    start_scheduler(run_immediately=True)
