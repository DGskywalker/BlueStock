#!/usr/bin/env python3
"""
CAGR Unit Test Suite (tests/kpi/test_cagr.py)
Contains 10 unit tests covering normal CAGR calculations and all 6 edge case flag handlers.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.analytics.cagr import calculate_cagr

class TestCAGREngine(unittest.TestCase):

    def test_01_normal_cagr_calculation_3yr(self):
        val, flag = calculate_cagr(100.0, 133.1, 3)
        self.assertEqual(flag, "NORMAL")
        self.assertEqual(val, 10.0)

    def test_02_normal_cagr_calculation_5yr(self):
        val, flag = calculate_cagr(100.0, 161.051, 5)
        self.assertEqual(flag, "NORMAL")
        self.assertEqual(val, 10.0)

    def test_03_decline_to_loss_flag_negative_end(self):
        val, flag = calculate_cagr(100.0, -50.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "DECLINE_TO_LOSS")

    def test_04_decline_to_loss_flag_zero_end(self):
        val, flag = calculate_cagr(100.0, 0.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "DECLINE_TO_LOSS")

    def test_05_turnaround_flag_negative_start(self):
        val, flag = calculate_cagr(-50.0, 100.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "TURNAROUND")

    def test_06_both_negative_flag(self):
        val, flag = calculate_cagr(-50.0, -20.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "BOTH_NEGATIVE")

    def test_07_zero_base_flag(self):
        val, flag = calculate_cagr(0.0, 0.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "ZERO_BASE")

    def test_08_insufficient_data_zero_years(self):
        val, flag = calculate_cagr(100.0, 200.0, 0)
        self.assertIsNone(val)
        self.assertEqual(flag, "INSUFFICIENT")

    def test_09_insufficient_data_none_values(self):
        val, flag = calculate_cagr(None, 200.0, 5)
        self.assertIsNone(val)
        self.assertEqual(flag, "INSUFFICIENT")

    def test_10_normal_high_growth_cagr(self):
        val, flag = calculate_cagr(100.0, 300.0, 3)
        self.assertEqual(flag, "NORMAL")
        self.assertEqual(val, 44.22)


if __name__ == "__main__":
    unittest.main()
