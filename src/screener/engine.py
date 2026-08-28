#!/usr/bin/env python3
"""
Financial Screener & Composite Scoring Engine (src/screener/engine.py)
Implements:
  - YAML configuration loading (config/screener_config.yaml)
  - 15 filterable financial metrics with Bank D/E carve-out & ICR "Debt Free" infinity handling
  - P10/P90 Winsorised Composite Quality Scoring (35% Profitability, 30% Cash Quality, 20% Growth, 15% Leverage)
  - Sector-relative score normalisation
  - 6 Preset Screeners: Quality Compounder, Value Pick, Growth Accelerator, Dividend Champion, Debt-Free Blue Chip, Turnaround Watch
"""

import os
import yaml
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

FINANCIALS_KEYWORDS = ["FINANCIAL", "BANK", "INSURANCE", "NBFC", "HOUSING FINANCE"]

def is_financials_row(row: pd.Series) -> bool:
    sec = str(row.get("sector", "") or "").upper()
    ind = str(row.get("industry", "") or "").upper()
    return any(k in sec or k in ind for k in FINANCIALS_KEYWORDS)

def load_screener_config(config_path: str = "config/screener_config.yaml") -> Dict[str, Any]:
    """Loads screener threshold parameters from YAML config."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    # Fallback dictionary if YAML file missing
    return {
        "presets": {
            "quality_compounder": {
                "name": "Quality Compounder",
                "filters": {"return_on_equity_pct_min": 15.0, "debt_to_equity_max": 1.0, "free_cash_flow_cr_min": 0.0, "revenue_cagr_5yr_min": 10.0}
            },
            "value_pick": {
                "name": "Value Pick",
                "filters": {"pe_ratio_max": 20.0, "pb_ratio_max": 3.0, "debt_to_equity_max": 2.0, "dividend_yield_min": 1.0}
            },
            "growth_accelerator": {
                "name": "Growth Accelerator",
                "filters": {"pat_cagr_5yr_min": 20.0, "revenue_cagr_5yr_min": 15.0, "debt_to_equity_max": 2.0}
            },
            "dividend_champion": {
                "name": "Dividend Champion",
                "filters": {"dividend_yield_min": 2.0, "dividend_payout_ratio_pct_max": 80.0, "free_cash_flow_cr_min": 0.0}
            },
            "debt_free_blue_chip": {
                "name": "Debt-Free Blue Chip",
                "filters": {"debt_to_equity_max": 0.0, "return_on_equity_pct_min": 12.0, "sales_min": 5000.0}
            },
            "turnaround_watch": {
                "name": "Turnaround Watch",
                "filters": {"revenue_cagr_3yr_min": 10.0, "free_cash_flow_cr_min": 0.0, "debt_to_equity_max": 2.0}
            }
        }
    }


def winsorize_series(series: pd.Series, p_low: float = 10.0, p_high: float = 90.0) -> pd.Series:
    """Clips extreme values at 10th and 90th percentiles before 0-100 scaling."""
    s_clean = series.dropna()
    if s_clean.empty:
        return series.fillna(0.0)
    low_val = np.percentile(s_clean, p_low)
    high_val = np.percentile(s_clean, p_high)
    if low_val == high_val:
        return series.fillna(low_val)
    return series.clip(lower=low_val, upper=high_val)


def scale_0_100(series: pd.Series, inverse: bool = False) -> pd.Series:
    """Scales a series to 0-100. If inverse=True, lower original values yield higher scores."""
    s_win = winsorize_series(series)
    min_val = s_win.min()
    max_val = s_win.max()
    if max_val == min_val:
        return pd.Series(50.0, index=series.index)
    scaled = ((s_win - min_val) / (max_val - min_val)) * 100.0
    return (100.0 - scaled) if inverse else scaled


def compute_composite_quality_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Winsorised Composite Quality Score (0-100 scale):
      - 35% Profitability: ROE (15%), ROCE (10%), NPM (10%)
      - 30% Cash Quality: FCF (15%), CFO/PAT (10%), FCF Positive (5%)
      - 20% Growth: Revenue CAGR (10%), PAT CAGR (10%)
      - 15% Leverage: D/E (10% inverse), ICR (5%)
    Includes sector-relative normalisation.
    """
    df_out = df.copy()

    # Fill default numeric columns if missing
    for col in ["return_on_equity_pct", "return_on_capital_employed_pct", "net_profit_margin_pct",
                "free_cash_flow_cr", "cfo_quality_score", "revenue_cagr_5yr", "pat_cagr_5yr",
                "debt_to_equity", "interest_coverage"]:
        if col not in df_out.columns:
            df_out[col] = 0.0

    # Sub-scores
    roe_score = scale_0_100(df_out["return_on_equity_pct"])
    roce_score = scale_0_100(df_out["return_on_capital_employed_pct"])
    npm_score = scale_0_100(df_out["net_profit_margin_pct"])
    prof_score = (0.15 * roe_score) + (0.10 * roce_score) + (0.10 * npm_score) # Max 35

    fcf_score = scale_0_100(df_out["free_cash_flow_cr"])
    cfo_pat_score = scale_0_100(df_out["cfo_quality_score"].fillna(1.0))
    fcf_pos_score = (df_out["free_cash_flow_cr"] > 0).astype(float) * 100.0
    cash_score = (0.15 * fcf_score) + (0.10 * cfo_pat_score) + (0.05 * fcf_pos_score) # Max 30

    rev_cagr_score = scale_0_100(df_out["revenue_cagr_5yr"].fillna(0.0))
    pat_cagr_score = scale_0_100(df_out["pat_cagr_5yr"].fillna(0.0))
    growth_score = (0.10 * rev_cagr_score) + (0.10 * pat_cagr_score) # Max 20

    de_score = scale_0_100(df_out["debt_to_equity"].fillna(0.0), inverse=True)
    icr_val = df_out["interest_coverage"].fillna(100.0) # Debt free infinity
    icr_score = scale_0_100(icr_val)
    lev_score = (0.10 * de_score) + (0.05 * icr_score) # Max 15

    raw_composite = prof_score + cash_score + growth_score + lev_score
    df_out["composite_quality_score"] = raw_composite.round(2)

    # Sector-relative adjustment
    if "sector" in df_out.columns:
        for sec, group in df_out.groupby("sector"):
            g_min, g_max = group["composite_quality_score"].min(), group["composite_quality_score"].max()
            if g_max > g_min:
                sec_scaled = ((group["composite_quality_score"] - g_min) / (g_max - g_min)) * 100.0
                df_out.loc[group.index, "sector_composite_score"] = sec_scaled.round(2)
            else:
                df_out.loc[group.index, "sector_composite_score"] = 50.0
    else:
        df_out["sector_composite_score"] = df_out["composite_quality_score"]

    return df_out


class ScreenerEngine:
    """Filter Engine evaluating financial thresholds across preset and custom rules."""

    def __init__(self, config_path: str = "config/screener_config.yaml"):
        self.config = load_screener_config(config_path)

    def filter_universe(self, df_ratios: pd.DataFrame, filters: Dict[str, float]) -> pd.DataFrame:
        """Filters DataFrame matching 15 possible threshold filters."""
        if df_ratios.empty:
            return df_ratios

        df = compute_composite_quality_score(df_ratios)
        mask = pd.Series(True, index=df.index)

        # 1. Return on Equity Min
        if "return_on_equity_pct_min" in filters:
            val = filters["return_on_equity_pct_min"]
            mask &= (df["return_on_equity_pct"].fillna(-999.0) >= val)

        # 2. Debt to Equity Max (Skip Financials Sector)
        if "debt_to_equity_max" in filters:
            val = filters["debt_to_equity_max"]
            is_fin_mask = df.apply(is_financials_row, axis=1)
            de_pass = (df["debt_to_equity"].fillna(0.0) <= val) | is_fin_mask
            mask &= de_pass

        # 3. Free Cash Flow Min
        if "free_cash_flow_cr_min" in filters:
            val = filters["free_cash_flow_cr_min"]
            mask &= (df["free_cash_flow_cr"].fillna(-99999.0) >= val)

        # 4. Revenue CAGR 5yr Min
        if "revenue_cagr_5yr_min" in filters:
            val = filters["revenue_cagr_5yr_min"]
            mask &= (df["revenue_cagr_5yr"].fillna(-999.0) >= val)

        # 5. Revenue CAGR 3yr Min
        if "revenue_cagr_3yr_min" in filters:
            val = filters["revenue_cagr_3yr_min"]
            mask &= (df["revenue_cagr_3yr"].fillna(-999.0) >= val)

        # 6. PAT CAGR 5yr Min
        if "pat_cagr_5yr_min" in filters:
            val = filters["pat_cagr_5yr_min"]
            mask &= (df["pat_cagr_5yr"].fillna(-999.0) >= val)

        # 7. Operating Profit Margin Min
        if "operating_profit_margin_pct_min" in filters:
            val = filters["operating_profit_margin_pct_min"]
            mask &= (df["operating_profit_margin_pct"].fillna(-999.0) >= val)

        # 8. P/E Ratio Max
        if "pe_ratio_max" in filters:
            val = filters["pe_ratio_max"]
            mask &= (df["pe_ratio"].fillna(999.0) <= val)

        # 9. P/B Ratio Max
        if "pb_ratio_max" in filters:
            val = filters["pb_ratio_max"]
            mask &= (df["pb_ratio"].fillna(999.0) <= val)

        # 10. Dividend Yield Min
        if "dividend_yield_min" in filters:
            val = filters["dividend_yield_min"]
            mask &= (df["dividend_payout_ratio_pct"].fillna(0.0) / 10.0 >= val) # Dividend yield proxy

        # 11. Dividend Payout Max
        if "dividend_payout_ratio_pct_max" in filters:
            val = filters["dividend_payout_ratio_pct_max"]
            mask &= (df["dividend_payout_ratio_pct"].fillna(0.0) <= val)

        # 12. Interest Coverage Min (Debt Free infinity handling)
        if "interest_coverage_min" in filters:
            val = filters["interest_coverage_min"]
            is_debt_free = (df["icr_label"] == "Debt Free")
            icr_pass = (df["interest_coverage"].fillna(999.0) >= val) | is_debt_free
            mask &= icr_pass

        # 13. Sales Min
        if "sales_min" in filters:
            val = filters["sales_min"]
            if "sales" in df.columns:
                mask &= (df["sales"].fillna(0.0) >= val)

        # 14. Asset Turnover Min
        if "asset_turnover_min" in filters:
            val = filters["asset_turnover_min"]
            mask &= (df["asset_turnover"].fillna(0.0) >= val)

        # 15. EPS CAGR Min
        if "eps_cagr_5yr_min" in filters:
            val = filters["eps_cagr_5yr_min"]
            mask &= (df["eps_cagr_5yr"].fillna(-999.0) >= val)

        filtered_df = df[mask].copy()
        return filtered_df.sort_values("composite_quality_score", ascending=False)

    def run_preset(self, df_ratios: pd.DataFrame, preset_key: str) -> pd.DataFrame:
        """Executes one of the 6 preset stock screeners."""
        presets = self.config.get("presets", {})
        if preset_key not in presets:
            raise ValueError(f"Preset '{preset_key}' not found in screener_config.yaml")
        filters = presets[preset_key].get("filters", {})
        return self.filter_universe(df_ratios, filters)
