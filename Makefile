# Bluestock Sprints 1, 2, 3 & 4 Build Automation Makefile

PYTHON = python3
DB_PATH = db/nifty100.db

.PHONY: all load ratios screener valuation test report dashboard api clean help

all: test load ratios screener valuation

load:
	@echo "=== [1/5] Generating Source Data & Running ETL Load Engine ==="
	$(PYTHON) src/etl/loader.py

ratios:
	@echo "=== [2/5] Executing Sprint 2 Financial Ratio Analytics Engine ==="
	$(PYTHON) generate_sprint2_ratios.py

screener:
	@echo "=== [3/5] Executing Sprint 3 Screener & Peer Comparison Engine ==="
	$(PYTHON) generate_sprint3_screener_peer.py

valuation:
	@echo "=== [4/5] Executing Sprint 4 Valuation Analytics Engine ==="
	$(PYTHON) generate_sprint4_valuation.py

test:
	@echo "=== Running All Unit Test Suites (75+ Unit Tests across ETL, KPI, Screener, Peer & Valuation) ==="
	$(PYTHON) -m unittest discover -s tests/etl -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/kpi -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/screener -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/peer -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/valuation -p "test_*.py"

report:
	@echo "=== Generating Final PDF Reports & Presentation Decks ==="
	$(PYTHON) generate_final_report.py
	$(PYTHON) generate_presentation.py

dashboard:
	@echo "=== Launching Interactive Streamlit Web Application ==="
	streamlit run app.py

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
	@echo "  make valuation - Executes Sprint 4 Valuation Engine (output/valuation_summary.xlsx)"
	@echo "  make test      - Executes 75+ unit tests across tests/etl, tests/kpi, tests/screener, tests/peer, tests/valuation"
	@echo "  make dashboard - Launches interactive Streamlit web dashboard"
	@echo "  make report    - Generates 18-page technical report & 12-slide presentation"
	@echo "  make clean     - Removes Python cache and temporary files"
