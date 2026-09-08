#!/usr/bin/env python3
"""
FastAPI Main Application Entry Point (src/api/main.py)
Imports all 7 routers under prefix /api/v1:
  - health.py
  - companies.py
  - screener.py
  - sectors.py
  - peers.py
  - valuation.py
  - portfolio.py
Run via: uvicorn src.api.main:app --port 8000
"""

import sys
import os
import time
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.abspath("."))

from src.api.routers import health, companies, screener, sectors, peers, valuation, portfolio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BlueStockAPI")

app = FastAPI(
    title="BlueStock Nifty 100 Financial Analytics REST API",
    description="Production REST API providing endpoints for stock screeners, peer comparison percentiles, ratio analytics, company profiles, and valuation metrics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Allows all origins for internal use)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(f"{request.method} {request.url.path} -> Status {response.status_code} ({duration} ms)")
    return response

# Mount Routers under /api/v1
app.include_router(health.router, prefix="/api/v1", tags=["Health & System"])
app.include_router(companies.router, prefix="/api/v1", tags=["Company Profile & Financials"])
app.include_router(screener.router, prefix="/api/v1", tags=["Stock Screener"])
app.include_router(sectors.router, prefix="/api/v1", tags=["Sector Analytics"])
app.include_router(peers.router, prefix="/api/v1", tags=["Peer Comparison"])
app.include_router(valuation.router, prefix="/api/v1", tags=["Valuation Metrics"])
app.include_router(portfolio.router, prefix="/api/v1", tags=["Portfolio Statistics"])

@app.get("/")
def root():
    return {
        "message": "Welcome to BlueStock Nifty 100 Financial Analytics REST API v1.0",
        "documentation": "/docs",
        "health_check": "/api/v1/health"
    }
