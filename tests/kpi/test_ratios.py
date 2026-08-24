#!/usr/bin/env python3
"""
Ratio Unit Test Suite (tests/kpi/test_ratios.py)
Contains 8 unit tests covering Net Profit Margin, ROE, ROCE, ROA, D/E debt-free 0, ICR debt-free None, ICR label, high D/E flag.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.analytics.ratios import (
    compute_net_profit_margin,
    compute_operating_profit_margin,
    compute_return_on_equity,
    compute_return_on_capital_employed,
    compute_return_on_assets,
    compute_debt_to_equity,
    compute_high_leverage_flag,
    compute_interest_coverage,
    compute_icr_warning_flag
)

class TestRatioEngine(unittest.TestCase):
    
    def test_01_net_profit_margin_normal_and_zero_sales(self):
        self.assertEqual(compute_net_profit_margin(100.0, 1000.0), 10.0)
        self.assertIsNone(compute_net_profit_margin(100.0, 0.0))

    def test_02_opm_cross_check(self):
        self.assertEqual(compute_operating_profit_margin(200.0, 1000.0), 20.0)
        self.assertIsNone(compute_operating_profit_margin(200.0, 0.0))

    def test_03_roe_normal_and_negative_equity(self):
        self.assertEqual(compute_return_on_equity(150.0, 100.0, 900.0), 15.0) # 150 / 1000 * 100
        self.assertIsNone(compute_return_on_equity(150.0, -100.0, 50.0)) # Negative equity

    def test_04_roce_normal_and_financials(self):
        self.assertEqual(compute_return_on_capital_employed(200.0, 20.0, 100.0, 400.0, 500.0), 22.0) # 220 / 1000 * 100
        self.assertIsNotNone(compute_return_on_capital_employed(200.0, 20.0, 100.0, 400.0, 500.0, is_financials=True))

    def test_05_roa_normal_and_zero_assets(self):
        self.assertEqual(compute_return_on_assets(100.0, 2000.0), 5.0)
        self.assertIsNone(compute_return_on_assets(100.0, 0.0))

    def test_06_debt_to_equity_debt_free_returns_zero(self):
        self.assertEqual(compute_debt_to_equity(0.0, 100.0, 400.0), 0.0)
        self.assertEqual(compute_debt_to_equity(None, 100.0, 400.0), 0.0)
        self.assertEqual(compute_debt_to_equity(500.0, 100.0, 400.0), 1.0)

    def test_07_icr_interest_zero_returns_none_and_debt_free_label(self):
        icr, label = compute_interest_coverage(200.0, 20.0, 0.0)
        self.assertIsNone(icr)
        self.assertEqual(label, "Debt Free")
        
        icr_normal, label_normal = compute_interest_coverage(200.0, 20.0, 50.0)
        self.assertEqual(icr_normal, 4.4)
        self.assertIsNone(label_normal)

    def test_08_high_leverage_flag_and_financials_suppression(self):
        self.assertTrue(compute_high_leverage_flag(6.0, is_financials=False))
        self.assertFalse(compute_high_leverage_flag(6.0, is_financials=True)) # Suppressed for Financials
        self.assertFalse(compute_high_leverage_flag(2.0, is_financials=False))


if __name__ == "__main__":
    unittest.main()
