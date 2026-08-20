#!/usr/bin/env python3
"""
ETL Unit Test Suite (tests/etl/test_normaliser.py)
Contains 35+ unit tests (20 for normalize_year, 15 for normalize_ticker).
Run via: python3 -m unittest tests/etl/test_normaliser.py or make test
"""

import unittest
from src.etl.normaliser import normalize_year, normalize_ticker

class TestETLNormaliser(unittest.TestCase):
    
    # -------------------------------------------------------------------------
    # 20 UNIT TESTS FOR normalize_year()
    # -------------------------------------------------------------------------
    def test_year_integer_standard(self):
        self.assertEqual(normalize_year(2023), 2023)

    def test_year_float_integer(self):
        self.assertEqual(normalize_year(2023.0), 2023)

    def test_year_string_standard(self):
        self.assertEqual(normalize_year("2023"), 2023)

    def test_year_fy_short(self):
        self.assertEqual(normalize_year("FY23"), 2023)

    def test_year_fy_hyphen(self):
        self.assertEqual(normalize_year("FY-23"), 2023)

    def test_year_fy_space(self):
        self.assertEqual(normalize_year("FY 2023"), 2023)

    def test_year_month_string_short(self):
        self.assertEqual(normalize_year("Mar 2023"), 2023)

    def test_year_month_string_full(self):
        self.assertEqual(normalize_year("March 2023"), 2023)

    def test_year_date_format_hyphen(self):
        self.assertEqual(normalize_year("31-03-2023"), 2023)

    def test_year_date_format_slash(self):
        self.assertEqual(normalize_year("2023/03/31"), 2023)

    def test_year_range_full(self):
        self.assertEqual(normalize_year("2022-2023"), 2023)

    def test_year_range_short(self):
        self.assertEqual(normalize_year("2022-23"), 2023)

    def test_year_range_slash(self):
        self.assertEqual(normalize_year("2022/23"), 2023)

    def test_year_short_2digit_string(self):
        self.assertEqual(normalize_year("23"), 2023)

    def test_year_short_2digit_apostrophe(self):
        self.assertEqual(normalize_year("'23"), 2023)

    def test_year_past_century(self):
        self.assertEqual(normalize_year("1998"), 1998)

    def test_year_fy_past_century(self):
        self.assertEqual(normalize_year("FY98"), 1998)

    def test_year_none_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_year(None)

    def test_year_empty_string_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_year("  ")

    def test_year_invalid_text_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_year("INVALID_YEAR")

    # -------------------------------------------------------------------------
    # 15 UNIT TESTS FOR normalize_ticker()
    # -------------------------------------------------------------------------
    def test_ticker_clean_uppercase(self):
        self.assertEqual(normalize_ticker("RELIANCE"), "RELIANCE")

    def test_ticker_lowercase_conversion(self):
        self.assertEqual(normalize_ticker("tcs"), "TCS")

    def test_ticker_whitespace_trimming(self):
        self.assertEqual(normalize_ticker("  hdfcbank  "), "HDFCBANK")

    def test_ticker_nse_suffix(self):
        self.assertEqual(normalize_ticker("INFY.NS"), "INFY")

    def test_ticker_bse_suffix(self):
        self.assertEqual(normalize_ticker("500180.BO"), "500180")

    def test_ticker_nse_full_suffix(self):
        self.assertEqual(normalize_ticker("SBIN.NSE"), "SBIN")

    def test_ticker_bse_full_suffix(self):
        self.assertEqual(normalize_ticker("SBIN.BSE"), "SBIN")

    def test_ticker_with_hyphen(self):
        self.assertEqual(normalize_ticker("BAJAJ-AUTO"), "BAJAJ-AUTO")

    def test_ticker_with_underscore(self):
        self.assertEqual(normalize_ticker("M_M"), "M_M")

    def test_ticker_numeric_code(self):
        self.assertEqual(normalize_ticker("500325"), "500325")

    def test_ticker_lowercase_with_suffix(self):
        self.assertEqual(normalize_ticker("ltim.ns"), "LTIM")

    def test_ticker_special_chars_stripped(self):
        self.assertEqual(normalize_ticker("ITC@#$"), "ITC")

    def test_ticker_none_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_ticker(None)

    def test_ticker_empty_string_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_ticker("   ")

    def test_ticker_nan_string_raises_error(self):
        with self.assertRaises(ValueError):
            normalize_ticker("NAN")


if __name__ == "__main__":
    unittest.main()
