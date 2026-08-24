#!/usr/bin/env python3
"""
Profitability, Leverage & Efficiency Ratio Engine (src/analytics/ratios.py)
Computes financial ratios with formula edge-case handling:
  - Net Profit Margin, OPM, ROE (negative equity handling), ROCE (bank carve-outs), ROA
  - Debt-to-Equity (debt-free returns 0.0), High Leverage Flag (suppressed for Financials)
  - Interest Coverage Ratio (interest=0 returns None with "Debt Free" label & ICR < 1.5 warning flag)
  - Net Debt & Asset Turnover
"""

from typing import Optional, Tuple

def compute_net_profit_margin(net_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """Net Profit Margin = net_profit / sales * 100. Returns None if sales == 0."""
    if sales is None or net_profit is None or sales <= 0:
        return None
    return round((net_profit / sales) * 100.0, 2)


def compute_operating_profit_margin(operating_profit: Optional[float], sales: Optional[float]) -> Optional[float]:
    """Operating Profit Margin = operating_profit / sales * 100. Returns None if sales == 0."""
    if sales is None or operating_profit is None or sales <= 0:
        return None
    return round((operating_profit / sales) * 100.0, 2)


def compute_return_on_equity(net_profit: Optional[float], equity_capital: Optional[float], reserves: Optional[float]) -> Optional[float]:
    """Return on Equity = net_profit / (equity_capital + reserves) * 100. Returns None if equity+reserves <= 0."""
    if net_profit is None or equity_capital is None:
        return None
    total_equity = equity_capital + (reserves if reserves is not None else 0.0)
    if total_equity <= 0:
        return None
    return round((net_profit / total_equity) * 100.0, 2)


def compute_return_on_capital_employed(operating_profit: Optional[float], other_income: Optional[float],
                                       equity_capital: Optional[float], reserves: Optional[float],
                                       borrowings: Optional[float], is_financials: bool = False) -> Optional[float]:
    """
    Return on Capital Employed = EBIT / (equity + reserves + borrowings) * 100.
    EBIT = operating_profit + (other_income or 0).
    For Financials broad_sector, sector-relative benchmark logic applies.
    """
    if operating_profit is None or equity_capital is None:
        return None
    ebit = operating_profit + (other_income if other_income is not None else 0.0)
    total_equity = equity_capital + (reserves if reserves is not None else 0.0)
    capital_employed = total_equity + (borrowings if borrowings is not None else 0.0)
    
    if capital_employed <= 0:
        return None
        
    roce = (ebit / capital_employed) * 100.0
    return round(roce, 2)


def compute_return_on_assets(net_profit: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """Return on Assets = net_profit / total_assets * 100. Returns None if total_assets <= 0."""
    if net_profit is None or total_assets is None or total_assets <= 0:
        return None
    return round((net_profit / total_assets) * 100.0, 2)


def compute_debt_to_equity(borrowings: Optional[float], equity_capital: Optional[float], reserves: Optional[float]) -> Optional[float]:
    """
    Debt-to-Equity = borrowings / (equity_capital + reserves).
    Returns 0.0 (not None) if borrowings == 0 or borrowings is None.
    Returns None if total_equity <= 0.
    """
    if borrowings is None or borrowings == 0:
        return 0.0
    if equity_capital is None:
        return None
    total_equity = equity_capital + (reserves if reserves is not None else 0.0)
    if total_equity <= 0:
        return None
    return round(borrowings / total_equity, 2)


def compute_high_leverage_flag(debt_to_equity: Optional[float], is_financials: bool = False) -> bool:
    """Returns True if D/E > 5 and company is NOT in Financials broad_sector."""
    if is_financials or debt_to_equity is None:
        return False
    return debt_to_equity > 5.0


def compute_interest_coverage(operating_profit: Optional[float], other_income: Optional[float], interest: Optional[float]) -> Tuple[Optional[float], Optional[str]]:
    """
    Interest Coverage Ratio = (operating_profit + other_income) / interest.
    Returns (None, "Debt Free") if interest == 0 or interest is None.
    """
    if interest is None or interest == 0:
        return None, "Debt Free"
    if operating_profit is None:
        return None, None
    ebit = operating_profit + (other_income if other_income is not None else 0.0)
    icr = ebit / interest
    return round(icr, 2), None


def compute_icr_warning_flag(icr: Optional[float]) -> bool:
    """Returns True if ICR < 1.5 (company at risk of interest coverage)."""
    if icr is None:
        return False
    return icr < 1.5


def compute_net_debt(borrowings: Optional[float], investments: Optional[float]) -> float:
    """Net Debt = borrowings - investments (using investments as liquid asset proxy)."""
    b = borrowings if borrowings is not None else 0.0
    inv = investments if investments is not None else 0.0
    return round(b - inv, 2)


def compute_asset_turnover(sales: Optional[float], total_assets: Optional[float]) -> Optional[float]:
    """Asset Turnover = sales / total_assets. Returns None if total_assets <= 0."""
    if sales is None or total_assets is None or total_assets <= 0:
        return None
    return round(sales / total_assets, 2)
