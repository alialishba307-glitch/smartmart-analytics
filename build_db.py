import sqlite3
import pandas as pd
from pathlib import Path

def build(clean_csv="data/clean/sales_clean.csv", db="data/smartmart.db"):
    df = pd.read_csv(clean_csv, parse_dates=["order_date"])
    Path(db).unlink(missing_ok=True)

    dim_product = df[["product_id", "product_name", "category"]].drop_duplicates("product_id")
    dim_customer = (df[df.customer_id != "UNKNOWN"][["customer_id", "customer_name", "city", "region"]]
                    .drop_duplicates("customer_id"))

    d = pd.DataFrame({"order_date": pd.date_range(df.order_date.min(), df.order_date.max())})
    dim_date = d.assign(year=d.order_date.dt.year, quarter=d.order_date.dt.quarter,
                        month=d.order_date.dt.month, month_name=d.order_date.dt.strftime("%b"),
                        day_name=d.order_date.dt.day_name())
    dim_date["order_date"] = dim_date["order_date"].dt.strftime("%Y-%m-%d")

    fact = df[["transaction_id", "order_date", "customer_id", "product_id", "city", "region",
               "channel", "quantity", "unit_price", "discount", "revenue"]].copy()
    fact["order_date"] = fact.order_date.dt.strftime("%Y-%m-%d")

    with sqlite3.connect(db) as con:
        fact.to_sql("fact_sales", con, index=False)
        dim_product.to_sql("dim_product", con, index=False)
        dim_customer.to_sql("dim_customer", con, index=False)
        dim_date.to_sql("dim_date", con, index=False)
        con.execute("""
            CREATE VIEW v_sales AS
            SELECT f.*, p.product_name, p.category,
                   COALESCE(c.customer_name,'Unknown') AS customer_name,
                   d.year, d.quarter, d.month, d.month_name
            FROM fact_sales f
            JOIN dim_product p ON f.product_id = p.product_id
            LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
            JOIN dim_date d ON f.order_date = d.order_date""")
        con.execute("CREATE INDEX idx_fact_date ON fact_sales(order_date)")
    print("Database built:", db)

if __name__ == "__main__":
    build()