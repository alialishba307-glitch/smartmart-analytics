import streamlit as st
import pandas as pd
from pathlib import Path
import db

st.set_page_config(page_title="SmartMart Analytics", layout="wide")

# Build the database on first run (needed on Streamlit Cloud if the DB isn't committed)
if not db.DB.exists():
    import clean, build_db
    Path("data/clean").mkdir(parents=True, exist_ok=True)
    out, _ = clean.clean(clean.load_raw())
    out.to_csv("data/clean/sales_clean.csv", index=False)
    build_db.build()

@st.cache_data
def options():
    return (db.run("SELECT MIN(order_date) mn, MAX(order_date) mx FROM fact_sales").iloc[0],
            db.run("SELECT DISTINCT category FROM dim_product ORDER BY 1").category.tolist(),
            db.run("SELECT DISTINCT region FROM fact_sales ORDER BY 1").region.tolist(),
            db.run("SELECT DISTINCT channel FROM fact_sales ORDER BY 1").channel.tolist())

@st.cache_data
def q(sql, params):
    return db.run(sql, params)

try:
    rng, cats, regs, chans = options()
except Exception as e:
    st.error(f"Could not load data: {e}")
    st.stop()

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
dates = st.sidebar.date_input("Date range", (pd.to_datetime(rng.mn), pd.to_datetime(rng.mx)))
if len(dates) != 2:
    st.warning("Select both a start and an end date.")
    st.stop()

f = {"start": str(dates[0]), "end": str(dates[1]),
     "categories": st.sidebar.multiselect("Category", cats),
     "regions": st.sidebar.multiselect("Region", regs),
     "channels": st.sidebar.multiselect("Channel", chans)}
w, p = db.where(f)
p = tuple(p)

st.title("SmartMart Sales Dashboard (Live)")

# ---------- KPI cards ----------
k = q(f"""SELECT COALESCE(SUM(revenue),0) revenue, COUNT(DISTINCT transaction_id) orders,
          COALESCE(SUM(quantity),0) units FROM v_sales WHERE {w}""", p).iloc[0]
if k.orders == 0:
    st.info("No data matches these filters.")
    st.stop()

cust = q(f"""SELECT customer_id, customer_name, COUNT(DISTINCT transaction_id) orders, SUM(revenue) revenue
             FROM v_sales WHERE {w} AND customer_id <> 'UNKNOWN' GROUP BY 1,2""", p)
repeat_rate = (cust.orders > 1).mean() if len(cust) else 0

c = st.columns(5)
c[0].metric("Revenue", f"Rs {k.revenue:,.0f}")
c[1].metric("Orders", f"{int(k.orders):,}")
c[2].metric("Avg order value", f"Rs {k.revenue / k.orders:,.0f}")
c[3].metric("Active customers", f"{len(cust):,}")
c[4].metric("Repeat rate", f"{repeat_rate:.1%}")

# ---------- Tabs ----------
t1, t2, t3, t4 = st.tabs(["Trends", "Products", "Regions", "Customers"])

with t1:
    grain = st.radio("View by", ["Daily", "Monthly", "Yearly"], index=1, horizontal=True)
    n = {"Daily": 10, "Monthly": 7, "Yearly": 4}[grain]
    trend = q(f"SELECT substr(order_date,1,{n}) period, SUM(revenue) revenue FROM v_sales WHERE {w} GROUP BY 1 ORDER BY 1", p)
    st.line_chart(trend.set_index("period"))

with t2:
    prod = q(f"SELECT product_name, category, SUM(revenue) revenue, SUM(quantity) units FROM v_sales WHERE {w} GROUP BY 1,2 ORDER BY revenue DESC", p)
    a, b = st.columns(2)
    a.subheader("Best sellers")
    a.bar_chart(prod.head(10).set_index("product_name")["revenue"])
    b.subheader("Underperformers")
    b.bar_chart(prod.tail(5).set_index("product_name")["revenue"])

with t3:
    reg = q(f"SELECT region, city, SUM(revenue) revenue FROM v_sales WHERE {w} GROUP BY 1,2 ORDER BY revenue DESC", p)
    st.bar_chart(reg.set_index("city")["revenue"])
    st.dataframe(reg)

with t4:
    if len(cust) == 0:
        st.info("No identified customers for these filters.")
    else:
        cust["type"] = cust.orders.map(lambda x: "Repeat" if x > 1 else "New")
        cut = cust.revenue.quantile([0.5, 0.9])
        cust["tier"] = cust.revenue.map(
            lambda r: "VIP (top 10%)" if r >= cut[0.9] else ("Regular" if r >= cut[0.5] else "Low value"))
        a, b = st.columns(2)
        a.subheader("New vs repeat")
        a.bar_chart(cust.type.value_counts())
        b.subheader("Value tiers")
        b.bar_chart(cust.tier.value_counts())
        st.subheader("Top customers")
        st.dataframe(cust.sort_values("revenue", ascending=False).head(20))

# ---------- Export ----------
detail = q(f"SELECT * FROM v_sales WHERE {w}", p)
st.sidebar.download_button("Download filtered data (CSV)", detail.to_csv(index=False),
                           "smartmart_filtered.csv", "text/csv")