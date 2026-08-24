# Bluestock Sprint 1 & Sprint 2 Build Automation Makefile

PYTHON = python3
DB_PATH = db/nifty100.db

.PHONY: all load ratios test report dashboard api clean help

all: test load ratios

load:
	@echo "=== [1/3] Generating Source Data & Running ETL Load Engine ==="
	$(PYTHON) src/etl/loader.py

ratios:
	@echo "=== [2/3] Executing Sprint 2 Financial Ratio Analytics Engine ==="
	$(PYTHON) generate_sprint2_ratios.py

test:
	@echo "=== Running ETL & KPI Unit Test Suites (55+ Unit Tests) ==="
	$(PYTHON) -m unittest discover -s tests/etl -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/kpi -p "test_*.py"

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
	@echo "  make test      - Executes 55+ unit tests across tests/etl and tests/kpi"
	@echo "  make report    - Generates 18-page technical report & 12-slide presentation"
	@echo "  make dashboard - Renders Power BI assets & HTML dashboard"
	@echo "  make api       - Executes REST API JSON extractor"
	@echo "  make clean     - Removes Python cache and temporary files"
