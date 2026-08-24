#!/usr/bin/env python3
"""
CAGR Analytics Engine (src/analytics/cagr.py)
Computes Compound Annual Growth Rates (CAGR) for Revenue, PAT, and EPS across 3Y, 5Y, and 10Y windows.
Handles all 6 CAGR edge cases:
  1. NORMAL (Positive -> Positive)
  2. DECLINE_TO_LOSS (Positive -> Negative/Zero)
  3. TURNAROUND (Negative/Zero -> Positive)
  4. BOTH_NEGATIVE (Negative -> Negative)
  5. ZERO_BASE (Start Value == 0)
  6. INSUFFICIENT (Data points < N years)
"""

from typing import Optional, Tuple, List, Dict
import pandas as pd

def calculate_cagr(start_val: Optional[float], end_val: Optional[float], n_years: int) -> Tuple[Optional[float], str]:
    """
    Computes CAGR = ((end_val / start_val) ** (1 / n_years) - 1) * 100.
    Returns (cagr_value, flag_label).
    """
    if n_years <= 0:
        return None, "INSUFFICIENT"
        
    if start_val is None or end_val is None:
        return None, "INSUFFICIENT"

    # Edge Case 5: Zero Base
    if start_val == 0:
        if end_val > 0:
            return None, "TURNAROUND"
        elif end_val < 0:
            return None, "DECLINE_TO_LOSS"
        else:
            return None, "ZERO_BASE"

    # Edge Case 2: Decline to Loss (Start > 0, End <= 0)
    if start_val > 0 and end_val <= 0:
        return None, "DECLINE_TO_LOSS"

    # Edge Case 3: Turnaround (Start < 0, End > 0)
    if start_val < 0 and end_val > 0:
        return None, "TURNAROUND"

    # Edge Case 4: Both Negative (Start < 0, End <= 0)
    if start_val < 0 and end_val <= 0:
        return None, "BOTH_NEGATIVE"

    # Edge Case 1: Normal Calculation (Start > 0, End > 0)
    try:
        ratio = end_val / start_val
        cagr = ((ratio ** (1.0 / float(n_years))) - 1.0) * 100.0
        return round(cagr, 2), "NORMAL"
    except Exception:
        return None, "INSUFFICIENT"


def compute_metric_cagr_for_company(df_metric: pd.DataFrame, company_id: int, value_col: str,
                                     n_years: int, target_year: int) -> Tuple[Optional[float], str]:
    """
    Computes metric CAGR over n_years window ending at target_year for a company.
    """
    start_year = target_year - n_years
    df_comp = df_metric[df_metric["company_id"] == company_id].sort_values("year")
    
    end_row = df_comp[df_comp["year"] == target_year]
    start_row = df_comp[df_comp["year"] == start_year]
    
    if end_row.empty or start_row.empty:
        return None, "INSUFFICIENT"
        
    end_val = end_row[value_col].values[0]
    start_val = start_row[value_col].values[0]
    
    return calculate_cagr(start_val, end_val, n_years)
