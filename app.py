#!/usr/bin/env python3
"""
Root Streamlit Application Entry Point (app.py)
Invokes src/dashboard/app.py multi-page dashboard.
Run via: streamlit run app.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath("."))

from src.dashboard import app as dashboard_app

if __name__ == "__main__":
    pass
