#!/usr/bin/env python3
"""
Cash Flow KPIs Unit Test Suite (tests/kpi/test_cashflow_kpis.py)
Contains 5 unit tests covering FCF, CFO Quality Score, CapEx Intensity, FCF Conversion, and 8-pattern Classifier.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.analytics.cashflow_kpis import (
    compute_free_cash_flow,
    compute_cfo_quality_score,
    compute_capex_intensity,
    compute_fcf_conversion,
    classify_capital_allocation_pattern
)

class TestCashflowKPIs(unittest.TestCase):

    def test_01_free_cash_flow(self):
        self.assertEqual(compute_free_cash_flow(500.0, -200.0), 300.0)
        self.assertEqual(compute_free_cash_flow(100.0, -300.0), -200.0)

    def test_02_cfo_quality_score(self):
        cfo_list = [120.0, 110.0, 130.0, 100.0, 140.0]
        pat_list = [100.0, 100.0, 100.0, 100.0, 100.0]
        score, label = compute_cfo_quality_score(cfo_list, pat_list)
        self.assertEqual(score, 1.2)
        self.assertEqual(label, "High Quality")

    def test_03_capex_intensity(self):
        intensity, label = compute_capex_intensity(-20.0, 1000.0) # 2% -> Asset Light
        self.assertEqual(intensity, 2.0)
        self.assertEqual(label, "Asset Light")

        intensity_heavy, label_heavy = compute_capex_intensity(-100.0, 1000.0) # 10% -> Capital Intensive
        self.assertEqual(intensity_heavy, 10.0)
        self.assertEqual(label_heavy, "Capital Intensive")

    def test_04_fcf_conversion(self):
        self.assertEqual(compute_fcf_conversion(300.0, 500.0), 60.0)
        self.assertIsNone(compute_fcf_conversion(300.0, 0.0))

    def test_05_capital_allocation_patterns(self):
        self.assertEqual(classify_capital_allocation_pattern(500.0, -200.0, -100.0), "Reinvestor")
        self.assertEqual(classify_capital_allocation_pattern(500.0, -200.0, -100.0, cfo_pat_ratio=1.5), "Shareholder Returns")
        self.assertEqual(classify_capital_allocation_pattern(-100.0, 50.0, 50.0), "Distress Signal")
        self.assertEqual(classify_capital_allocation_pattern(-100.0, -50.0, 150.0), "Growth Funded by Debt")


if __name__ == "__main__":
    unittest.main()
