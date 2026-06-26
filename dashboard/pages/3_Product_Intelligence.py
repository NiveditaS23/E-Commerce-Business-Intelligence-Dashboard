import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

st.set_page_config(
    page_title="Sales Performance",
    page_icon="📦",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]
orders = pd.read_csv(
    BASE_DIR / "data/raw/olist_orders_dataset.csv"
)

payments = pd.read_csv(
    BASE_DIR / "data/raw/olist_order_payments_dataset.csv"
)

items = pd.read_csv(
    BASE_DIR / "data/raw/olist_order_items_dataset.csv"
)

products = pd.read_csv(
    BASE_DIR / "data/raw/olist_products_dataset.csv"
)

translation = pd.read_csv(
    BASE_DIR / "data/raw/product_category_name_translation.csv"
)
products = products.merge(
    translation,
    on="product_category_name",
    how="left"
)

product_sales = items.merge(
    products,
    on="product_id",
    how="left"
)

st.title("📦 Product Intelligence")



col1, col2, col3, col4 = st.columns(4)

total_products = products["product_id"].nunique()

avg_price = items["price"].mean()

total_categories = (
    products["product_category_name"]
    .nunique()
)

total_items_sold = len(items)

col1.metric(
    "Products",
    f"{total_products:,}"
)

col2.metric(
    "Avg Price",
    f"${avg_price:.2f}"
)

col3.metric(
    "Categories",
    f"{total_categories:,}"
)

col4.metric(
    "Items Sold",
    f"{total_items_sold:,}"
)

total_revenue = payments[
    "payment_value"
].sum()

total_orders = orders[
    "order_id"
].nunique()

avg_order_value = (
    total_revenue / total_orders
)



st.markdown("---")

orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

revenue_data = orders.merge(
    payments,
    on="order_id",
    how="left"
)

#st.markdown("---")

# TOP PRODUCTS BY REVENUE

top_products = (
    product_sales
    .groupby(
        "product_category_name_english"
    )["price"]
    .sum()
    .reset_index()
    .sort_values(
        "price",
        ascending=False
    )
    .head(10)
)

fig_products = px.bar(
    top_products,
    x="product_category_name_english",
    y="price",
    title="Top 10 Products by Revenue"
)

fig_products.update_layout(
    template="plotly_white",
    height=500,
    xaxis_title="Category",
    yaxis_title="Revenue",
    xaxis_tickangle=-45
)


orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

orders["order_estimated_delivery_date"] = pd.to_datetime(
    orders["order_estimated_delivery_date"]
)


orders["late"] = (
    orders[
        "order_delivered_customer_date"
    ]
    >
    orders[
        "order_estimated_delivery_date"
    ]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

delivery_status = pd.DataFrame({
    "Status": [
        "On Time",
        "Late"
    ],
    "Count": [
        (~orders["late"]).sum(),
        orders["late"].sum()
    ]
})

fig_late = px.bar(
    delivery_status,
    x="Status",
    y="Count",
    title="On-Time vs Late Deliveries"
)

fig_late.update_layout(
    template="plotly_white",
    height=450
)

status_data = (
    orders["order_status"]
    .value_counts()
    .reset_index()
)

status_data.columns = [
    "Status",
    "Count"
]

fig_status = px.bar(
    status_data,
    x="Status",
    y="Count",
    title="Order Status Distribution"
)

fig_status.update_layout(
    template="plotly_white",
    height=450
)

orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    -
    orders["order_purchase_timestamp"]
).dt.days

fig_delivery = px.histogram(
    orders,
    x="delivery_days",
    title="Delivery Time Distribution"
)

fig_delivery.update_layout(
    template="plotly_white",
    height=450
)

# --------------------------------------------------
# DASHBOARD LAYOUT
# --------------------------------------------------

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_products,
        use_container_width=True,
        key="top_products"
    )

with right:

    st.plotly_chart(
        fig_status,
        use_container_width=True,
        key="order_status"
    )

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_delivery,
        use_container_width=True,
        key="delivery_distribution"
    )

with right:

    st.plotly_chart(
        fig_late,
        use_container_width=True,
        key="late_delivery"
    )

    st.markdown("----")

st.subheader("📌 Product Insights")

st.info(f"""
• Top-performing categories drive a significant share of revenue.

• Average product price is ${avg_price:.2f}.

• Portfolio contains {total_products:,} products.

• Business operates across {total_categories:,} categories.

• Delivery performance can be monitored using the distribution chart above.
""")



