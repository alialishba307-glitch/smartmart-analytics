import json
import pandas as pd
from pathlib import Path

REQUIRED = ["transaction_id", "order_date", "product_id", "quantity", "unit_price"]

def load_raw(folder="data/raw"):
    files = sorted(Path(folder).glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    return pd.concat([pd.read_csv(f) for f in files], ignore_index=True)

def clean(df):
    report = {"rows_raw": len(df)}

    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    # 1. standardise text (trim spaces, consistent capitalisation)
    for c in ["product_name", "category", "channel", "city", "region", "customer_name"]:
        if c in df:
            df[c] = df[c].astype("string").str.strip().str.title()

    # 2. dates
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    report["invalid_dates"] = int(df["order_date"].isna().sum())

    # 3. drop rows missing mandatory fields
    before = len(df)
    df = df.dropna(subset=REQUIRED)
    report["missing_required_dropped"] = before - len(df)

    # 4. invalid numbers (negative quantity, bad price, discount outside 0-1)
    before = len(df)
    df = df[(df.quantity > 0) & (df.unit_price > 0) & df.discount.between(0, 1)]
    report["invalid_numeric_dropped"] = before - len(df)

    # 5. duplicates: same transaction_id = duplicate
    before = len(df)
    df = df.drop_duplicates(subset="transaction_id", keep="first")
    report["duplicates_removed"] = before - len(df)

    # 6. one consistent name/category per product_id
    canon = df.groupby("product_id")[["product_name", "category"]].agg(lambda s: s.mode().iat[0])
    df = df.drop(columns=["product_name", "category"]).join(canon, on="product_id")

    # 7. missing customers: keep the sale, flag the customer as UNKNOWN
    report["missing_customer_rows"] = int(df.customer_id.isna().sum())
    df["customer_id"] = df.customer_id.fillna("UNKNOWN")
    df["customer_name"] = df.customer_name.fillna("Unknown")

    # 8. revenue KPI
    df["revenue"] = (df.unit_price * df.quantity * (1 - df.discount)).round(2)
    report["rows_clean"] = len(df)
    return df, report

if __name__ == "__main__":
    out, rep = clean(load_raw())
    Path("data/clean").mkdir(parents=True, exist_ok=True)
    out.to_csv("data/clean/sales_clean.csv", index=False)
    with open("data/clean/quality_report.json", "w") as fh:
        json.dump(rep, fh, indent=2)
    print(rep)