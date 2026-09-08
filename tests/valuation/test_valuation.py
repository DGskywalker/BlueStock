#!/usr/bin/env python3
"""
Valuation Engine Unit Test Suite (tests/valuation/test_valuation.py)
Tests FCF yield calculation, 5-year median P/E, sector median P/E comparison, and Caution/Discount/Fair overvaluation classification.
"""

import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.analytics.valuation import compute_valuation_metrics

class TestValuationEngine(unittest.TestCase):

    def setUp(self):
        self.df_ratios = pd.DataFrame([
            {"company_id": 1, "year": 2024, "pe_ratio": 45.0, "pb_ratio": 5.0, "free_cash_flow_cr": 200.0},
            {"company_id": 2, "year": 2024, "pe_ratio": 12.0, "pb_ratio": 1.5, "free_cash_flow_cr": 800.0},
            {"company_id": 3, "year": 2024, "pe_ratio": 20.0, "pb_ratio": 2.2, "free_cash_flow_cr": 300.0}
        ])
        
        self.df_companies = pd.DataFrame([
            {"company_id": 1, "ticker": "EXPENSIVE", "company_name": "Expensive Ltd", "sector": "IT"},
            {"company_id": 2, "ticker": "CHEAP", "company_name": "Cheap Ltd", "sector": "IT"},
            {"company_id": 3, "ticker": "FAIR", "company_name": "Fair Ltd", "sector": "IT"}
        ])
        
        self.df_pnl = pd.DataFrame([
            {"company_id": 1, "year": 2024, "sales": 2000.0},
            {"company_id": 2, "year": 2024, "sales": 4000.0},
            {"company_id": 3, "year": 2024, "sales": 3000.0}
        ])

    def test_01_valuation_metrics_calculation(self):
        df_val = compute_valuation_metrics(self.df_ratios, self.df_companies, self.df_pnl)
        self.assertEqual(len(df_val), 3)
        self.assertIn("fcf_yield_pct", df_val.columns)
        self.assertIn("valuation_flag", df_val.columns)

    def test_02_overvaluation_caution_flag(self):
        df_val = compute_valuation_metrics(self.df_ratios, self.df_companies, self.df_pnl)
        exp_row = df_val[df_val["ticker"] == "EXPENSIVE"].iloc[0]
        # Sector median P/E is 20.0. 45.0 > (20.0 * 1.5 = 30.0) -> Caution!
        self.assertEqual(exp_row["valuation_flag"], "Caution")

    def test_03_overvaluation_discount_flag(self):
        df_val = compute_valuation_metrics(self.df_ratios, self.df_companies, self.df_pnl)
        cheap_row = df_val[df_val["ticker"] == "CHEAP"].iloc[0]
        # Sector median P/E is 20.0. 12.0 < (20.0 * 0.7 = 14.0) -> Discount!
        self.assertEqual(cheap_row["valuation_flag"], "Discount")

    def test_04_overvaluation_fair_flag(self):
        df_val = compute_valuation_metrics(self.df_ratios, self.df_companies, self.df_pnl)
        fair_row = df_val[df_val["ticker"] == "FAIR"].iloc[0]
        self.assertEqual(fair_row["valuation_flag"], "Fair")


if __name__ == "__main__":
    unittest.main()
