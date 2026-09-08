#!/usr/bin/env python3
"""
FastAPI REST API Unit Test Suite (tests/api/test_api.py)
Tests all 16 endpoints using FastAPI TestClient.
"""

import unittest
import sys
import os
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath("."))

from src.api.main import app

class TestFastAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_health_endpoint(self):
        res = self.client.get("/api/v1/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("db_row_counts", data)

    def test_02_companies_list(self):
        res = self.client.get("/api/v1/companies")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 92)

    def test_03_company_profile(self):
        res = self.client.get("/api/v1/companies/TCS")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["ticker"], "TCS")

        res_404 = self.client.get("/api/v1/companies/INVALID_TICKER")
        self.assertEqual(res_404.status_code, 404)

    def test_04_screener_endpoint(self):
        res = self.client.get("/api/v1/screener?min_roe=15")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("match_count", data)

        res_400 = self.client.get("/api/v1/screener?min_roe=-5")
        self.assertEqual(res_400.status_code, 400)

    def test_05_sectors_endpoint(self):
        res = self.client.get("/api/v1/sectors")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 9)

        res_sec = self.client.get("/api/v1/sectors/IT/companies")
        self.assertEqual(res_sec.status_code, 200)
        sec_data = res_sec.json()
        self.assertGreater(len(sec_data), 0)


if __name__ == "__main__":
    unittest.main()
