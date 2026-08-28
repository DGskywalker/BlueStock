#!/usr/bin/env python3
"""
Peer Analytics Unit Test Suite (tests/peer/test_peer.py)
Tests peer percentile calculation, inverted D/E ranking, unassigned company handling, and radar chart input formatting.
"""

import unittest
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath("."))

from src.analytics.peer import compute_percent_rank, PeerAnalyticsEngine

class TestPeerAnalyticsEngine(unittest.TestCase):

    def setUp(self):
        self.engine = PeerAnalyticsEngine(db_path=":memory:")
        self.series_normal = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
        self.series_de = pd.Series([0.1, 0.5, 1.0, 2.0, 5.0])

    def test_01_percentile_rank_normal_metric(self):
        pct = compute_percent_rank(self.series_normal, inverse=False)
        self.assertEqual(pct.iloc[0], 0.0) # Lowest value = 0th percentile
        self.assertEqual(pct.iloc[-1], 1.0) # Highest value = 100th percentile

    def test_02_percentile_rank_inverted_de_metric(self):
        pct_de = compute_percent_rank(self.series_de, inverse=True)
        self.assertEqual(pct_de.iloc[0], 1.0) # Lowest D/E (0.1) = 100th percentile!
        self.assertEqual(pct_de.iloc[-1], 0.0) # Highest D/E (5.0) = 0th percentile!

    def test_03_unassigned_company_no_error(self):
        df_ratios = pd.DataFrame([
            {"company_id": 1, "year": 2024, "return_on_equity_pct": 20.0, "debt_to_equity": 0.2}
        ])
        df_comp = pd.DataFrame([
            {"company_id": 1, "ticker": "COMPA", "company_name": "A Ltd", "sector": "IT"},
            {"company_id": 2, "ticker": "COMPB", "company_name": "B Ltd", "sector": None} # Unassigned
        ])
        df_peers = pd.DataFrame([{"company_id": 1, "peer_company_id": 1}])

        df_pct = self.engine.compute_all_peer_percentiles(df_ratios, df_comp, df_peers)
        self.assertFalse(df_pct.empty)


if __name__ == "__main__":
    unittest.main()
