import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
Path("data/raw").mkdir(parents=True, exist_ok=True)

cities = {"Karachi": "South", "Lahore": "Central", "Multan": "Central",
          "Islamabad": "North", "Peshawar": "North", "Quetta": "West"}

products = pd.DataFrame([
    ("P01", "Smartphone", "Electronics", 45000), ("P02", "Laptop", "Electronics", 120000),
    ("P03", "Headphones", "Electronics", 8000), ("P04", "Smart Watch", "Electronics", 15000),
    ("P05", "T-Shirt", "Clothing", 1500), ("P06", "Jeans", "Clothing", 3500),
    ("P07", "Jacket", "Clothing", 6500), ("P08", "Sneakers", "Clothing", 7000),
    ("P09", "Microwave Oven", "Home Appliances", 22000), ("P10", "Air Fryer", "Home Appliances", 18000),
    ("P11", "Blender", "Home Appliances", 6000), ("P12", "Vacuum Cleaner", "Home Appliances", 25000),
    ("P13", "Rice 5kg", "Grocery", 1400), ("P14", "Cooking Oil 5L", "Grocery", 3200),
    ("P15", "Tea 900g", "Grocery", 1500), ("P16", "Sugar 5kg", "Grocery", 700),
], columns=["product_id", "product_name", "category", "unit_price"])

customers = pd.DataFrame({
    "customer_id": [f"C{i:04d}" for i in range(1, 801)],
    "customer_name": [f"Customer {i}" for i in range(1, 801)],
})
customers["city"] = rng.choice(list(cities), len(customers))

N = 6000
df = pd.DataFrame({
    "transaction_id": [f"TXN{i:06d}" for i in range(1, N + 1)],
    "order_date": pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 1095, N), unit="D"),
    "customer_id": rng.choice(customers.customer_id, N),
    "product_id": rng.choice(products.product_id, N),
    "quantity": rng.integers(1, 5, N),
    "discount": rng.choice([0, 0.05, 0.10, 0.20], N, p=[0.6, 0.2, 0.15, 0.05]),
    "channel": rng.choice(["Online", "Store"], N, p=[0.45, 0.55]),
})
df = df.merge(products, on="product_id").merge(customers, on="customer_id")
df["region"] = df["city"].map(cities)

# ---- inject data quality problems ----
dups = df.sample(int(0.03 * N), random_state=1)
df = pd.concat([df, dups], ignore_index=True)          # duplicate transactions

miss = df.sample(frac=0.02, random_state=2).index
df.loc[miss, ["customer_id", "customer_name"]] = np.nan  # missing customers

idx = df.sample(frac=0.05, random_state=3).index
df.loc[idx, "product_name"] = df.loc[idx, "product_name"].str.upper() + " "  # inconsistent names

df.loc[df.sample(frac=0.01, random_state=4).index, "quantity"] = -1  # invalid quantity

df = df.sort_values("order_date")
for year, part in df.groupby(df.order_date.dt.year):
    part.to_csv(f"data/raw/sales_{year}.csv", index=False)

print("Raw files created:", len(df), "rows")