import pandas as pd
import pytest
from clean import clean

def sample():
    return pd.DataFrame({
        "transaction_id": ["T1", "T1", "T2", "T3"],
        "order_date": ["2024-01-01", "2024-01-01", "2024-01-02", "bad-date"],
        "customer_id": ["C1", "C1", None, "C2"],
        "customer_name": ["A", "A", None, "B"],
        "product_id": ["P1"] * 4,
        "product_name": ["Phone", "PHONE ", "Phone", "Phone"],
        "category": ["Electronics"] * 4,
        "unit_price": [100] * 4,
        "quantity": [2, 2, -1, 1],
        "discount": [0.1, 0.1, 0, 0],
        "channel": ["Online"] * 4,
        "city": ["Karachi"] * 4,
        "region": ["South"] * 4,
    })

def test_duplicates_removed():
    out, rep = clean(sample())
    assert out.transaction_id.is_unique
    assert rep["duplicates_removed"] == 1

def test_invalid_rows_dropped():
    out, _ = clean(sample())
    assert (out.quantity > 0).all()

def test_revenue_formula():
    out, _ = clean(sample())
    assert out.iloc[0].revenue == 180   # 100 * 2 * (1 - 0.1)

def test_missing_column_raises():
    with pytest.raises(ValueError):
        clean(sample().drop(columns=["quantity"]))