import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

st.set_page_config(
    page_title="Logistics Intelligence",
    page_icon="🌍",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

customers = pd.read_csv(
    BASE_DIR / "data/raw/olist_customers_dataset.csv"
)

orders = pd.read_csv(
    BASE_DIR / "data/raw/olist_orders_dataset.csv"
)

payments = pd.read_csv(
    BASE_DIR / "data/raw/olist_order_payments_dataset.csv"
)

customer_orders = orders.merge(
    customers,
    on="customer_id",
    how="left"
)

order_revenue = customer_orders.merge(
    payments,
    on="order_id",
    how="left"
)

st.title("🌍 Logistics Intelligence")

total_states = customers[
    "customer_state"
].nunique()

top_state = (
    order_revenue
    .groupby("customer_state")["payment_value"]
    .sum()
    .idxmax()
)

top_state_revenue = (
    order_revenue
    .groupby("customer_state")["payment_value"]
    .sum()
    .max()
)

# Revenue by State
state_revenue = (
    order_revenue
    .groupby("customer_state")["payment_value"]
    .sum()
    .reset_index()
    .sort_values(
        "payment_value",
        ascending=False
    )
)

# Top 10 States
top_states = (
    state_revenue
    .head(10)
)

# Create chart
fig_top_states = px.bar(
    top_states,
    x="payment_value",
    y="customer_state",
    orientation="h",
    title="Top 10 States by Revenue"
)

fig_top_states.update_layout(
    template="plotly_white",
    height=500
)

top_state_customers = (
    customers["customer_state"]
    .value_counts()
    .idxmax()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "States Served",
    total_states
)

col2.metric(
    "Top Revenue State",
    top_state
)

col3.metric(
    "Top State Revenue",
    f"${top_state_revenue/1000000:.2f}M"
)

col4.metric(
    "Most Customers",
    top_state_customers
)

st.markdown("---")

fig_revenue = px.bar(
    top_states,
    x="customer_state",
    y="payment_value",
    title="Top 10 States by Revenue"
)

fig_revenue.update_layout(
    template="plotly_white",
    height=500,
    xaxis_title="State",
    yaxis_title="Revenue"
)

fig_revenue.update_layout(
    template="plotly_white",
    height=500,
    yaxis_title="State",
    xaxis_title="Revenue"
)

fig_revenue.update_layout(
    height=500,
    template="plotly_white"
)

fig_revenue.update_yaxes(
    tickprefix="$"
)

state_aov = (
    order_revenue
    .groupby("customer_state")
    .agg({
        "payment_value": "sum",
        "order_id": "nunique"
    })
    .reset_index()
)

state_aov["AOV"] = (
    state_aov["payment_value"]
    /
    state_aov["order_id"]
)

state_aov = (
    state_aov
    .sort_values(
        "AOV",
        ascending=False
    )
    .head(10)
)

fig_aov = px.bar(
    state_aov,
    x="customer_state",
    y="AOV",
    title="Top States by Average Order Value"
)

fig_aov.update_layout(
    template="plotly_white",
    height=500
)


state_customers = (
    customers
    .groupby("customer_state")
    .size()
    .reset_index(name="Customers")
    .sort_values(
        "Customers",
        ascending=False
    )
)

fig_customers = px.bar(
    state_customers,
    x="customer_state",
    y="Customers",
    title="Customers by State"
)

fig_customers.update_layout(
    height=500,
    template="plotly_white"
)

# ------------------------------------
# CHART ROW 1
# ------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_customers,
        use_container_width=True,
        key="state_customers"
    )

with right:

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
        key="top_states_revenue"
    )

# ------------------------------------
# CHART ROW 2
# ------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_aov,
        use_container_width=True,
        key="state_aov"
    )

st.markdown("---")

st.subheader("📌 Regional Insights")

st.info(f"""
• Business operates across {total_states} states.

• Highest revenue is generated from {top_state}.

• {top_state_customers} contains the largest customer base.

• Geographic concentration can be used to prioritize marketing investments.

• State-level analysis helps identify expansion opportunities.
""")