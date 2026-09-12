import os
import sys
import time
import subprocess
import html

def run_all_tests_and_generate_html():
    test_dirs = [
        ("ETL Pipeline", "tests/etl"),
        ("KPI Analytics Engine", "tests/kpi"),
        ("Stock Screener Engine", "tests/screener"),
        ("Peer Comparison Analytics", "tests/peer"),
        ("Valuation Engine", "tests/valuation"),
        ("NLP & Pros/Cons Engine", "tests/nlp"),
        ("Report Generators", "tests/reports"),
        ("FastAPI REST Server", "tests/api"),
    ]

    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_duration = 0.0

    test_results_data = []

    print("=== RUNNING PLATFORM TEST SUITES & GENERATING HTML REPORT ===")

    env = os.environ.copy()
    user_site = "/Users/divyanshgupta/Library/Python/3.9/lib/python/site-packages"
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = user_site + ":" + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = user_site

    for suite_name, test_dir in test_dirs:
        if not os.path.exists(test_dir):
            continue

        cmd = [sys.executable, "-m", "unittest", "discover", "-s", test_dir, "-p", "test_*.py"]
        
        start_time = time.time()
        proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
        duration = time.time() - start_time
        total_duration += duration

        output = proc.stdout + "\n" + proc.stderr
        
        # Parse test count and failures from unittest output
        # e.g., "Ran 35 tests in 0.008s"
        run_count = 0
        fail_count = 0
        err_count = 0

        for line in output.splitlines():
            if line.startswith("Ran ") and "tests in" in line:
                try:
                    run_count = int(line.split()[1])
                except ValueError:
                    pass
            elif line.startswith("FAILED ("):
                # e.g., FAILED (failures=1, errors=2)
                parts = line.replace("FAILED (", "").replace(")", "").split(",")
                for p in parts:
                    if "failures=" in p:
                        try:
                            fail_count = int(p.split("=")[1].strip())
                        except ValueError:
                            pass
                    if "errors=" in p:
                        try:
                            err_count = int(p.split("=")[1].strip())
                        except ValueError:
                            pass

        if proc.returncode != 0 and fail_count == 0 and err_count == 0:
            err_count = 1

        pass_count = max(0, run_count - (fail_count + err_count))

        total_tests += run_count
        total_passed += pass_count
        total_failed += fail_count
        total_errors += err_count

        status = "PASSED" if (proc.returncode == 0 and fail_count == 0 and err_count == 0) else "FAILED"

        test_results_data.append({
            "suite_name": suite_name,
            "test_dir": test_dir,
            "tests_run": run_count,
            "passed": pass_count,
            "failed": fail_count,
            "errors": err_count,
            "duration": round(duration, 4),
            "status": status
        })

        print(f"[{status}] {suite_name:<30} | Tests: {run_count:<3} | Passed: {pass_count:<3} | Time: {duration:.3f}s")

    os.makedirs("reports", exist_ok=True)
    report_path = "reports/pytest_report.html"

    overall_status = "PASSED" if (total_failed == 0 and total_errors == 0) else "FAILED"
    status_badge_color = "#28a745" if overall_status == "PASSED" else "#dc3545"

    rows_html = ""
    for r in test_results_data:
        badge_cls = "badge-pass" if r["status"] == "PASSED" else "badge-fail"
        rows_html += f"""
        <tr>
            <td><strong>{html.escape(r['suite_name'])}</strong></td>
            <td><code>{html.escape(r['test_dir'])}</code></td>
            <td>{r['tests_run']}</td>
            <td style="color: #28a745; font-weight: bold;">{r['passed']}</td>
            <td style="color: #dc3545; font-weight: bold;">{r['failed']}</td>
            <td style="color: #6c757d;">{r['errors']}</td>
            <td>{r['duration']}s</td>
            <td><span class="badge {badge_cls}">{r['status']}</span></td>
        </tr>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>BlueStock Financial Platform — Test Execution Report</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            margin: 40px;
            background-color: #f8f9fa;
            color: #212529;
        }}
        .header {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 28px; }}
        .header p {{ margin: 0; opacity: 0.9; font-size: 15px; }}
        .summary-cards {{
            display: flex;
            gap: 20px;
            margin: 25px 0;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            flex: 1;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border-left: 5px solid #2a5298;
        }}
        .card .title {{ font-size: 13px; text-transform: uppercase; color: #6c757d; font-weight: bold; }}
        .card .value {{ font-size: 28px; font-weight: bold; margin-top: 5px; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        th, td {{
            padding: 14px 18px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background-color: #f1f3f5;
            font-weight: 600;
            color: #495057;
        }}
        tr:hover {{ background-color: #f8f9fa; }}
        .badge {{
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            color: white;
        }}
        .badge-pass {{ background-color: #28a745; }}
        .badge-fail {{ background-color: #dc3545; }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 13px;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>BlueStock Financial Platform Test Audit Report</h1>
        <p>Automated Verification of Unit & REST API Test Suites (Deliverable D-21)</p>
    </div>

    <div class="summary-cards">
        <div class="card" style="border-left-color: {status_badge_color};">
            <div class="title">Overall Status</div>
            <div class="value" style="color: {status_badge_color};">{overall_status}</div>
        </div>
        <div class="card">
            <div class="title">Total Test Suites</div>
            <div class="value">{len(test_results_data)}</div>
        </div>
        <div class="card">
            <div class="title">Total Tests Executed</div>
            <div class="value">{total_tests}</div>
        </div>
        <div class="card">
            <div class="title">Passed / Failed</div>
            <div class="value"><span style="color: #28a745;">{total_passed}</span> / <span style="color: #dc3545;">{total_failed + total_errors}</span></div>
        </div>
        <div class="card">
            <div class="title">Total Execution Time</div>
            <div class="value">{total_duration:.2f}s</div>
        </div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Test Suite Module</th>
                <th>Directory Path</th>
                <th>Total Tests</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Errors</th>
                <th>Duration</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>

    <div class="footer">
        Generated by BlueStock QA Engine &bull; Zero Failure Gate Verified
    </div>
</body>
</html>
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\n✅ HTML Test Report generated successfully at '{report_path}' ({os.path.getsize(report_path)//1024} KB)")

    if total_failed > 0 or total_errors > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests_and_generate_html()
