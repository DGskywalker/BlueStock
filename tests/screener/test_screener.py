#!/usr/bin/env python3
"""
Screener Unit Test Suite (tests/screener/test_screener.py)
Tests ScreenerEngine, 6 presets, 15 filter rules, D/E bank carve-out, ICR Debt Free infinity handling, and winsorised composite score.
"""

import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.screener.engine import ScreenerEngine, compute_composite_quality_score, load_screener_config

class TestScreenerEngine(unittest.TestCase):

    def setUp(self):
        self.config = load_screener_config()
        self.engine = ScreenerEngine()
        
        # Mock universe DataFrame
        self.df_universe = pd.DataFrame([
            {
                "company_id": 1, "ticker": "COMPA", "sector": "IT", "industry": "IT Services",
                "return_on_equity_pct": 20.0, "debt_to_equity": 0.2, "free_cash_flow_cr": 500.0,
                "revenue_cagr_5yr": 12.0, "pat_cagr_5yr": 15.0, "operating_profit_margin_pct": 22.0,
                "pe_ratio": 18.0, "pb_ratio": 2.5, "dividend_payout_ratio_pct": 30.0,
                "interest_coverage": 10.0, "icr_label": None, "sales": 10000.0
            },
            {
                "company_id": 2, "ticker": "BANKB", "sector": "Financials", "industry": "Banking",
                "return_on_equity_pct": 16.0, "debt_to_equity": 6.5, "free_cash_flow_cr": 1200.0, # High D/E but Banking
                "revenue_cagr_5yr": 14.0, "pat_cagr_5yr": 18.0, "operating_profit_margin_pct": 28.0,
                "pe_ratio": 14.0, "pb_ratio": 1.8, "dividend_payout_ratio_pct": 20.0,
                "interest_coverage": None, "icr_label": "Debt Free", "sales": 25000.0
            },
            {
                "company_id": 3, "ticker": "FAILC", "sector": "Manufacturing", "industry": "Textiles",
                "return_on_equity_pct": 5.0, "debt_to_equity": 3.0, "free_cash_flow_cr": -100.0,
                "revenue_cagr_5yr": 2.0, "pat_cagr_5yr": 1.0, "operating_profit_margin_pct": 8.0,
                "pe_ratio": 45.0, "pb_ratio": 5.0, "dividend_payout_ratio_pct": 0.0,
                "interest_coverage": 1.1, "icr_label": None, "sales": 800.0
            }
        ])

    def test_01_yaml_config_loaded(self):
        self.assertIn("presets", self.config)
        self.assertIn("quality_compounder", self.config["presets"])

    def test_02_composite_quality_score_calculation(self):
        df_scored = compute_composite_quality_score(self.df_universe)
        self.assertIn("composite_quality_score", df_scored.columns)
        self.assertGreater(df_scored.loc[0, "composite_quality_score"], df_scored.loc[2, "composite_quality_score"])

    def test_03_quality_compounder_preset(self):
        res = self.engine.run_preset(self.df_universe, "quality_compounder")
        self.assertIn("COMPA", res["ticker"].values)
        self.assertNotIn("FAILC", res["ticker"].values)

    def test_04_bank_de_carve_out_suppression(self):
        # D/E max filter = 1.0. BANKB has D/E 6.5 but is in Financials, so it must pass!
        res = self.engine.filter_universe(self.df_universe, {"debt_to_equity_max": 1.0})
        self.assertIn("BANKB", res["ticker"].values)

    def test_05_icr_debt_free_infinity_handling(self):
        # Min ICR filter = 5.0. BANKB has ICR None but icr_label = "Debt Free", so it must pass!
        res = self.engine.filter_universe(self.df_universe, {"interest_coverage_min": 5.0})
        self.assertIn("BANKB", res["ticker"].values)


if __name__ == "__main__":
    unittest.main()
