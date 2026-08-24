#!/usr/bin/env python3
"""
Cash Flow KPIs & Capital Allocation Engine (src/analytics/cashflow_kpis.py)
Computes:
  - Free Cash Flow (FCF = CFO + CFI)
  - CFO Quality Score (5-year CFO / PAT ratio: High Quality, Moderate, Accrual Risk)
  - CapEx Intensity (abs(CFI) / Sales * 100: Asset Light, Moderate, Capital Intensive)
  - FCF Conversion Rate (FCF / Operating Profit * 100)
  - 8-Pattern Capital Allocation Classifier based on sign of (CFO, CFI, CFF)
"""

from typing import Optional, Tuple, List

def compute_free_cash_flow(cfo: Optional[float], cfi: Optional[float]) -> Optional[float]:
    """Free Cash Flow = CFO + CFI (CFI is typically negative for capex)."""
    if cfo is None or cfi is None:
        return None
    return round(cfo + cfi, 2)


def compute_cfo_quality_score(cfo_history: List[float], pat_history: List[float]) -> Tuple[Optional[float], str]:
    """
    Computes CFO / PAT ratio averaged over available 5-year history.
    Classification:
      - > 1.0: High Quality
      - 0.5 - 1.0: Moderate
      - < 0.5: Accrual Risk
    """
    if not cfo_history or not pat_history or len(cfo_history) != len(pat_history):
        return None, "Accrual Risk"
        
    valid_ratios = []
    for cfo, pat in zip(cfo_history, pat_history):
        if pat is not None and pat > 0 and cfo is not None:
            valid_ratios.append(cfo / pat)
            
    if not valid_ratios:
        return None, "Accrual Risk"
        
    avg_score = sum(valid_ratios) / len(valid_ratios)
    avg_score_rounded = round(avg_score, 2)
    
    if avg_score > 1.0:
        label = "High Quality"
    elif avg_score >= 0.5:
        label = "Moderate"
    else:
        label = "Accrual Risk"
        
    return avg_score_rounded, label


def compute_capex_intensity(cfi: Optional[float], sales: Optional[float]) -> Tuple[Optional[float], str]:
    """
    CapEx Intensity = abs(cfi) / sales * 100.
    Classification:
      - < 3%: Asset Light
      - 3 - 8%: Moderate
      - > 8%: Capital Intensive
    """
    if cfi is None or sales is None or sales <= 0:
        return None, "Asset Light"
        
    capex = abs(cfi)
    intensity = (capex / sales) * 100.0
    intensity_rounded = round(intensity, 2)
    
    if intensity < 3.0:
        label = "Asset Light"
    elif intensity <= 8.0:
        label = "Moderate"
    else:
        label = "Capital Intensive"
        
    return intensity_rounded, label


def compute_fcf_conversion(fcf: Optional[float], operating_profit: Optional[float]) -> Optional[float]:
    """FCF Conversion Rate = FCF / operating_profit * 100. Returns None if operating_profit <= 0."""
    if fcf is None or operating_profit is None or operating_profit <= 0:
        return None
    return round((fcf / operating_profit) * 100.0, 2)


def classify_capital_allocation_pattern(cfo: Optional[float], cfi: Optional[float], cff: Optional[float],
                                         cfo_pat_ratio: Optional[float] = None) -> str:
    """
    Classifies 8 capital allocation patterns based on sign of (CFO, CFI, CFF):
      - (+, -, -): Reinvestor (or Shareholder Returns if high CFO/PAT > 1.2)
      - (+, +, -): Liquidating Assets
      - (-, +, +): Distress Signal
      - (-, -, +): Growth Funded by Debt
      - (+, +, +): Cash Accumulator
      - (-, -, -): Pre-Revenue
      - (+, -, +): Mixed
    """
    if cfo is None or cfi is None or cff is None:
        return "Mixed"
        
    cfo_sign = "+" if cfo >= 0 else "-"
    cfi_sign = "+" if cfi >= 0 else "-"
    cff_sign = "+" if cff >= 0 else "-"
    
    pattern = (cfo_sign, cfi_sign, cff_sign)
    
    if pattern == ("+", "-", "-"):
        if cfo_pat_ratio is not None and cfo_pat_ratio > 1.2:
            return "Shareholder Returns"
        return "Reinvestor"
    elif pattern == ("+", "+", "-"):
        return "Liquidating Assets"
    elif pattern == ("-", "+", "+"):
        return "Distress Signal"
    elif pattern == ("-", "-", "+"):
        return "Growth Funded by Debt"
    elif pattern == ("+", "+", "+"):
        return "Cash Accumulator"
    elif pattern == ("-", "-", "-"):
        return "Pre-Revenue"
    elif pattern == ("+", "-", "+"):
        return "Mixed"
    else:
        return "Mixed"
