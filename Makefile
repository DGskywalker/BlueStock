# Bluestock Sprints 1, 2, 3, 4, 5 & 6 Build Automation Makefile

PYTHON = python3
DB_PATH = db/nifty100.db

.PHONY: all load ratios screener valuation nlp pdfs cluster api_server docs test report dashboard api clean help

all: test load ratios screener valuation nlp pdfs cluster docs

load:
	@echo "=== [1/7] Generating Source Data & Running ETL Load Engine ==="
	$(PYTHON) src/etl/loader.py

ratios:
	@echo "=== [2/7] Executing Sprint 2 Financial Ratio Analytics Engine ==="
	$(PYTHON) generate_sprint2_ratios.py

screener:
	@echo "=== [3/7] Executing Sprint 3 Screener & Peer Comparison Engine ==="
	$(PYTHON) generate_sprint3_screener_peer.py

valuation:
	@echo "=== [4/7] Executing Sprint 4 Valuation Analytics Engine ==="
	$(PYTHON) generate_sprint4_valuation.py

nlp:
	@echo "=== [5/7] Executing Sprint 5 NLP & Auto Pros/Cons Generator ==="
	$(PYTHON) generate_sprint5_nlp_reports.py

pdfs:
	@echo "=== [6/7] Executing Sprint 5 Batch PDF Tearsheet & Sector Report Generator ==="
	$(PYTHON) generate_sprint5_nlp_reports.py

cluster:
	@echo "=== [7/7] Executing Sprint 6 KMeans Clustering & Final Sign-Off Pipeline ==="
	$(PYTHON) generate_sprint6_final.py

api_server:
	@echo "=== Launching FastAPI REST Server on http://localhost:8000 ==="
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

docs:
	@echo "=== Exporting OpenAPI Specification & Analyst User Guide PDF ==="
	$(PYTHON) generate_sprint6_final.py

test:
	@echo "=== Running All Unit & API Test Suites (80+ Tests across ETL, KPI, Screener, Peer, Valuation, NLP, Reports & API) ==="
	$(PYTHON) -m unittest discover -s tests/etl -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/kpi -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/screener -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/peer -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/valuation -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/nlp -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/reports -p "test_*.py"
	$(PYTHON) -m unittest discover -s tests/api -p "test_*.py"

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
	rm -rf __pycache__ */__pycache__ */*/__pycache__ .pytest_cache .ipynb_checkpoints output/temp_charts output/temp_test_reports
	@echo "Clean completed."

help:
	@echo "Available Makefile targets:"
	@echo "  make load       - Executes source data generation, 16 DQ rules, and populates nifty100.db"
	@echo "  make ratios     - Executes Sprint 2 Financial Ratio Engine & populates financial_ratios table"
	@echo "  make screener   - Executes Sprint 3 Stock Screener Engine & Peer Comparison Analytics"
	@echo "  make valuation  - Executes Sprint 4 Valuation Engine (output/valuation_summary.xlsx)"
	@echo "  make nlp        - Executes Sprint 5 NLP Parser & Auto Pros/Cons Generator"
	@echo "  make pdfs       - Batch generates 92 company tearsheet PDFs & 11 sector PDF reports"
	@echo "  make cluster    - Executes Sprint 6 KMeans Clustering & Final Sign-Off Pipeline"
	@echo "  make api_server - Launches FastAPI REST server on localhost:8000"
	@echo "  make test       - Executes 80+ unit and API tests across all test packages"
	@echo "  make dashboard  - Launches interactive Streamlit web dashboard"
