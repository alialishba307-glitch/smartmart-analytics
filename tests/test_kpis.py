import pandas as pd
import db

def test_total_revenue_matches_csv():
    csv = pd.read_csv("data/clean/sales_clean.csv")
    sql = db.run("SELECT SUM(revenue) r FROM v_sales").r[0]
    assert abs(sql - csv.revenue.sum()) < 0.01

def test_order_count_matches():
    csv = pd.read_csv("data/clean/sales_clean.csv")
    assert db.run("SELECT COUNT(DISTINCT transaction_id) n FROM v_sales").n[0] == csv.transaction_id.nunique()

def test_no_duplicate_ids():
    assert db.run("SELECT COUNT(*)-COUNT(DISTINCT transaction_id) d FROM fact_sales").d[0] == 0