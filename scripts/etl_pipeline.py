#!/usr/bin/env python3
"""
Master ETL Pipeline Script (scripts/etl_pipeline.py)
Executes data ingestion, cleaning, daily NAV forward-fill, and SQLite star schema database loading.
"""

import os
import sys

def main():
    print("Executing Master ETL Pipeline...")
    os.system("python3 clean_data.py")
    os.system("python3 load_sqlite.py")
    print("ETL Pipeline Execution Complete!")

if __name__ == "__main__":
    main()
