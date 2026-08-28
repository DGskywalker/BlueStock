# Bluestock Sprints 1, 2 & 3 Build Automation Makefile

PYTHON = python3
DB_PATH = db/nifty100.db

.PHONY: all load ratios screener test report dashboard api clean help

all: test load ratios screener

load:
	@echo "=== [1/4] Generating Source Data & Running ETL Load Engine ==="
	$(PYTHON) src/etl/loader.py

ratios:
	@echo "=== [2/4] Executing Sprint 2 Financial Ratio Analytics Engine ==="
	$(PYTHON) generate_sprint2_ratios.py

screener:
	@echo "=== [3/4] Executing Sprint 3 Screener & Peer Comparison Engine ==="
	$(PYTHON) generate_sprint3_screener_peer.py

test:
	@echo "=== Running All Unit Test Suites (70+ Unit Tests across ETL, KPI, Screener & Peer) ==="
	$(PYTHON) -m unittest discover -s tests/etl -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/kpi -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/screener -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/peer -p "test_*.py"

report:
	@echo "=== Generating Final PDF Reports & Presentation Decks ==="
	$(PYTHON) generate_final_report.py
	$(PYTHON) generate_presentation.py

dashboard:
	@echo "=== Generating Power BI Assets & Launching Dashboard ==="
	$(PYTHON) generate_dashboard_assets.py

api:
	@echo "=== Running REST API Data Extraction ==="
	$(PYTHON) scripts/api_json_extractor.py

clean:
	@echo "=== Cleaning Generated Cache & Temporary Artifacts ==="
	rm -rf __pycache__ */__pycache__ */*/__pycache__ .pytest_cache .ipynb_checkpoints
	@echo "Clean completed."

help:
	@echo "Available Makefile targets:"
	@echo "  make load      - Executes source data generation, 16 DQ rules, and populates nifty100.db"
	@echo "  make ratios    - Executes Sprint 2 Financial Ratio Engine & populates financial_ratios table"
	@echo "  make screener  - Executes Sprint 3 Stock Screener Engine & Peer Comparison Analytics"
	@echo "  make test      - Executes 70+ unit tests across tests/etl, tests/kpi, tests/screener, tests/peer"
	@echo "  make report    - Generates 18-page technical report & 12-slide presentation"
	@echo "  make dashboard - Renders Power BI assets & HTML dashboard"
	@echo "  make api       - Executes REST API JSON extractor"
	@echo "  make clean     - Removes Python cache and temporary files"
