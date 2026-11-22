import pandas as pd
import db

csv = pd.read_csv("data/clean/sales_clean.csv")

print("--- SQL KPIs ---")
print(db.run("""SELECT SUM(revenue) AS revenue, COUNT(DISTINCT transaction_id) AS orders,
                SUM(revenue)/COUNT(DISTINCT transaction_id) AS aov, SUM(quantity) AS units
                FROM v_sales"""))

print("\n--- pandas KPIs (should match) ---")
print({"revenue": round(csv.revenue.sum(), 2), "orders": csv.transaction_id.nunique(),
       "aov": round(csv.revenue.sum() / csv.transaction_id.nunique(), 2), "units": int(csv.quantity.sum())})

print("\n--- Top 5 products ---")
print(db.run("SELECT product_name, SUM(revenue) AS revenue FROM v_sales GROUP BY 1 ORDER BY 2 DESC LIMIT 5"))

print("\n--- Revenue by region ---")
print(db.run("SELECT region, SUM(revenue) AS revenue FROM v_sales GROUP BY 1 ORDER BY 2 DESC"))