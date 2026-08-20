# Bluestock Sprint 1 Build Automation Makefile

PYTHON = python3
DB_PATH = db/nifty100.db

.PHONY: all load ratios test report dashboard api clean help

all: test load

load:
	@echo "=== [1/2] Generating Source Data & Running ETL Load Engine ==="
	$(PYTHON) src/etl/loader.py

test:
	@echo "=== Running ETL Unit Test Suite (35+ Tests) ==="
	$(PYTHON) -m unittest discover -s tests/etl -p "test_*.py"

ratios:
	@echo "=== Computing Financial Ratios & Performance Analytics ==="
	$(PYTHON) generate_performance_analytics.py

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
	@echo "  make test      - Executes 35+ unit tests (20 normalize_year, 15 normalize_ticker)"
	@echo "  make ratios    - Computes financial ratios and composite scorecards"
	@echo "  make report    - Generates 18-page technical report & 12-slide presentation"
	@echo "  make dashboard - Renders Power BI assets & HTML dashboard"
	@echo "  make api       - Executes REST API JSON extractor"
	@echo "  make clean     - Removes Python cache and temporary files"
