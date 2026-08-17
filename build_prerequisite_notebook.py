import os
import nbformat as nbf

nb = nbf.v4.new_notebook()
nb["cells"] = [
    nbf.v4.new_markdown_cell("# 06 REST API & JSON Data Extraction\n\nCalls public financial REST API endpoints (`mfapi.in`), inspects nested JSON responses, parses records using Pandas, computes daily percentage returns, and exports structured CSV dataset to `data/processed/api_extracted_data.csv`."),
    nbf.v4.new_code_cell("""import os, requests, pandas as pd

url = "https://api.mfapi.in/mf/119551"
res = requests.get(url)
data = res.json()

print("JSON Keys:", list(data.keys()))
print("Meta Information:", data["meta"])

df = pd.DataFrame(data["data"])
df["nav"] = pd.to_numeric(df["nav"], errors="coerce")
df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y")
df = df.sort_values("date").reset_index(drop=True)
df["daily_return_pct"] = df["nav"].pct_change() * 100.0

out_csv = os.path.join("..", "data", "processed", "api_extracted_data.csv") if os.path.exists("../data") else os.path.join("data", "processed", "api_extracted_data.csv")
df.to_csv(out_csv, index=False)
print("Saved extracted API data shape:", df.shape)
df.tail(10)
""")
]

with open(os.path.join("notebooks", "06_api_data_extraction.ipynb"), "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("Saved notebooks/06_api_data_extraction.ipynb!")
