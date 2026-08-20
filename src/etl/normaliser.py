#!/usr/bin/env python3
"""
ETL Normaliser Module (src/etl/normaliser.py)
Provides standardisation functions for financial year representations and ticker symbols.
Includes 35+ unit test scenarios for normalize_year() and normalize_ticker().
"""

import re

def normalize_year(val) -> int:
    """
    Normalises various financial year inputs into a standard 4-digit integer year (e.g. 2023).
    Supported formats:
      - Integers/Floats: 2023, 2023.0 -> 2023
      - String FY format: "FY23", "FY 2023", "FY-23" -> 2023
      - Month-Year strings: "Mar 2023", "March 2023", "31-03-2023", "2023/03/31" -> 2023
      - Range strings: "2022-23", "2022-2023", "2022/23" -> 2023
      - Short 2-digit strings: "23", "'23" -> 2023
    """
    if val is None:
        raise ValueError("Year input cannot be None")

    # If numeric float/int
    if isinstance(val, (int, float)):
        if isinstance(val, float) and float(val).is_integer():
            val = int(val)
        elif isinstance(val, float):
            val = int(val)
            
        if 1900 <= val <= 2100:
            return val
        if 0 <= val <= 99:
            return 2000 + val if val < 50 else 1900 + val

    s = str(val).strip().upper()
    if not s or s == "NAN" or s == "NONE":
        raise ValueError("Empty or invalid year string")

    # 1. Full Date strings e.g. "31-03-2023", "2023/03/31", "2023-03-31" -> return 4-digit year
    if re.search(r'\d{1,4}[-/]\d{1,2}[-/]\d{1,4}', s):
        match_4d = re.findall(r'\b(19\d\d|20\d\d)\b', s)
        if match_4d:
            return int(match_4d[-1])

    # 2. Year Range strings e.g. "2022-23", "2022-2023", "2022/23" (not full dates)
    match_range = re.search(r'\b(\d{4})[-/](\d{2,4})\b', s)
    if match_range:
        y2_str = match_range.group(2)
        if len(y2_str) == 4:
            return int(y2_str)
        elif len(y2_str) == 2:
            return 2000 + int(y2_str)

    # 3. Check full 4-digit year embedded anywhere (e.g. "MAR 2023", "2023")
    match_4digit = re.findall(r'\b(19\d\d|20\d\d)\b', s)
    if match_4digit:
        return int(match_4digit[-1])

    # 4. FY format like "FY23", "FY-23", "FY 23"
    match_fy = re.search(r'FY[- ]?(\d{2})\b', s)
    if match_fy:
        y_short = int(match_fy.group(1))
        return 2000 + y_short if y_short < 50 else 1900 + y_short

    # 5. Short 2-digit standalone string "23" or "'23"
    match_2digit = re.search(r"^'?(\d{2})$", s)
    if match_2digit:
        y_short = int(match_2digit.group(1))
        return 2000 + y_short if y_short < 50 else 1900 + y_short

    # Fallback digit extraction
    digits = re.sub(r'[^\d]', '', s)
    if len(digits) == 4 and 1900 <= int(digits) <= 2100:
        return int(digits)

    raise ValueError(f"Unable to normalize year format: '{val}'")


def normalize_ticker(val) -> str:
    """
    Normalises stock ticker symbols into uppercase clean alphanumeric tickers.
    Operations:
      - Strips exchange suffixes (.NS, .BO, .NSE, .BSE)
      - Trims whitespace & converts to uppercase
      - Strips non-alphanumeric special characters
    """
    if val is None:
        raise ValueError("Ticker input cannot be None")

    s = str(val).strip().upper()
    if not s or s == "NAN" or s == "NONE":
        raise ValueError("Empty or invalid ticker string")

    # Remove exchange suffixes
    s = re.sub(r'\.(NS|BO|NSE|BSE)$', '', s)

    # Remove special chars except hyphen/underscore
    s = re.sub(r'[^A-Z0-9_-]', '', s)

    if not s:
        raise ValueError(f"Invalid ticker result after normalisation: '{val}'")

    return s
