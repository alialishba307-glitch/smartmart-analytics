# SmartMart Analytics

Sales analytics dashboard for a retail company, built with Python, SQLite and Streamlit and deployed on free-tier cloud services only.

**Live app:** https://smartmart-analytics.streamlit.app

## Business problem
SmartMart sells electronics, clothing, home appliances and grocery through stores and online. Sales data sits in separate CSV files and reports are prepared manually. This project cleans the data, stores it in a SQL database and gives management an interactive dashboard.

## Architecture
raw CSVs -> clean.py -> clean CSV -> build_db.py -> SQLite star schema -> SQL queries -> Streamlit app -> GitHub -> Streamlit Community Cloud

## KPI definitions
| KPI | Definition |
|---|---|
| Revenue | unit_price x quantity x (1 - discount) |
| Orders | count of distinct transaction_id |
| Average order value | Revenue / Orders |
| Active customers | distinct known customer_id |
| Repeat rate | customers with 2+ orders / active customers |
| New vs repeat | 1 order in the filtered period = New, otherwise Repeat |

## Data quality (from quality_report.json)
Raw rows 6,180 -> clean rows 5,941: 62 invalid rows removed, 177 duplicate transactions removed, 122 sales with missing customers kept as UNKNOWN.

## How to run locally
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python generate_data.py
python clean.py
python build_db.py
streamlit run app.py
```

## Tests
`python -m pytest -v` runs 7 tests (cleaning rules and SQL vs pandas KPI matching). All pass.

## Deployment
1. Project pushed to a public GitHub repository.
2. Deployed from share.streamlit.io (repository, branch main, main file app.py).
3. Pushing to GitHub redeploys the app automatically.

## Free-tier limits and cloud usage
- Streamlit Community Cloud: apps go to sleep after a period of inactivity and need a click to wake; each app has limited CPU and memory; the repository must be on GitHub.
- GitHub free: single files are limited to 100 MB.
- SQLite: runs inside the app with no separate server. It is read-only here and does not scale to many concurrent writers.
- Cost: 0. No paid services are used.
- Measured usage: database file size 0.63 MB, 5,941 clean rows, app load time about 3 seconds.
## Limitations and upgrade path
- Data is synthetic and one transaction holds one product.
- The repeat rate is very high because there are only 800 customers for about 5,900 orders.
- New CSV files must be re-cleaned before they appear in the dashboard.
- When the data outgrows SQLite, move to a free-tier cloud database (Supabase, Neon or BigQuery) and change only db.py.