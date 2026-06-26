import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Executive Overview",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# PATH
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

customers = pd.read_csv(
    BASE_DIR / "data/raw/olist_customers_dataset.csv"
)

orders = pd.read_csv(
    BASE_DIR / "data/raw/olist_orders_dataset.csv"
)

payments = pd.read_csv(
    BASE_DIR / "data/raw/olist_order_payments_dataset.csv"
)

products = pd.read_csv(
    BASE_DIR / "data/raw/olist_products_dataset.csv"
)

items = pd.read_csv(
    BASE_DIR / "data/raw/olist_order_items_dataset.csv"
)

translation = pd.read_csv(
    BASE_DIR / "data/raw/product_category_name_translation.csv"
)

rfm_segments = pd.read_csv(
    BASE_DIR / "data/processed/rfm_segments.csv"
)

# --------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------

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

customer_orders = orders.merge(
    customers,
    on="customer_id",
    how="left"
)

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Filters")

state_filter = st.sidebar.selectbox(
    "State",
    ["All"] + sorted(
        customers["customer_state"].unique().tolist()
    )
)

category_filter = st.sidebar.selectbox(
    "Category",
    ["All"] + sorted(
        product_sales[
            "product_category_name_english"
        ].dropna().unique().tolist()
    )
)

segment_filter = st.sidebar.selectbox(
    "Customer Segment",
    ["All"] + sorted(
        rfm_segments["Segment"]
        .unique()
        .tolist()
    )
)

# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_customers = customers.copy()
filtered_product_sales = product_sales.copy()
filtered_rfm = rfm_segments.copy()
filtered_customer_orders = customer_orders.copy()

if state_filter != "All":

    filtered_customers = filtered_customers[
        filtered_customers["customer_state"]
        == state_filter
    ]

    filtered_customer_orders = (
        filtered_customer_orders[
            filtered_customer_orders["customer_state"]
            == state_filter
        ]
    )

if category_filter != "All":

    filtered_product_sales = (
        filtered_product_sales[
            filtered_product_sales[
                "product_category_name_english"
            ] == category_filter
        ]
    )

if segment_filter != "All":

    filtered_rfm = filtered_rfm[
        filtered_rfm["Segment"]
        == segment_filter
    ]

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📊 Executive Dashboard")
# --------------------------------------------------
# KPI ROW
# --------------------------------------------------

# Convert dates
orders['order_delivered_customer_date'] = pd.to_datetime(
    orders['order_delivered_customer_date']
)

orders['order_estimated_delivery_date'] = pd.to_datetime(
    orders['order_estimated_delivery_date']
)

# Keep only delivered orders with valid dates
delivered_orders = filtered_customer_orders.dropna(
    subset=[
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]
)

# Calculate late delivery %
late_percentage = (
    (
        delivered_orders['order_delivered_customer_date']
        >
        delivered_orders['order_estimated_delivery_date']
    ).mean()
) * 100

col1, col2, col3, col4, col5 = st.columns(5)

revenue_data = filtered_customer_orders.merge(
    payments,
    on="order_id",
    how="left"
)

total_revenue = revenue_data[
    "payment_value"
].sum()

col1.metric(
    "Revenue",
    f"${total_revenue/1000000:.2f}M"
)
total_customers = filtered_customers[
    "customer_unique_id"
].nunique()

total_orders = filtered_customer_orders[
    "order_id"
].nunique()

col2.metric(
    "Customers",
    f"{total_customers:,}"
)

col3.metric(
    "Orders",
    f"{total_orders:,}"
)
aov = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)

col4.metric(
    "AOV",
    f"${aov:.2f}"
)
col5.metric(
    "Late Deliveries",
    f"{late_percentage:.2f}%"
)

st.markdown("---")

sales_state = (
    filtered_customer_orders
    .merge(
        payments,
        on="order_id",
        how="left"
    )
    .groupby("customer_state")["payment_value"]
    .sum()
    .reset_index()
)
sales_state = sales_state.sort_values(
    "payment_value",
    ascending=False
)

# --------------------------------------------------
# HERO CHART
# --------------------------------------------------

filtered_customer_orders["order_purchase_timestamp"] = pd.to_datetime(
    filtered_customer_orders["order_purchase_timestamp"]
)

monthly_orders = (
    filtered_customer_orders
    .groupby(
        filtered_customer_orders[
            "order_purchase_timestamp"
        ].dt.to_period("M")
    )
    .size()
    .reset_index(name="Orders")
)

monthly_orders[
    "order_purchase_timestamp"
] = monthly_orders[
    "order_purchase_timestamp"
].astype(str)

fig_trend = px.line(
    monthly_orders,
    x="order_purchase_timestamp",
    y="Orders",
    title="Monthly Order Trend"
)

fig_trend.update_layout(
    height=500
)

st.plotly_chart(
    fig_trend,
    use_container_width=True,
    key="monthly_trend"
)
# --------------------------------------------------
# DATA
# --------------------------------------------------

segment_data = (
    filtered_rfm["Segment"]
    .value_counts()
    .reset_index()
)

segment_data.columns = [
    "Segment",
    "Count"
]

category_data = (
    filtered_product_sales
    .groupby(
        "product_category_name_english"
    )["price"]
    .sum()
    .sort_values(
        ascending=False
    )
    .head(10)
    .reset_index()
)

# --------------------------------------------------
# CHARTS ROW
# --------------------------------------------------

left, right = st.columns(2)

with left:

    fig_segment = px.bar(
        segment_data,
        x="Segment",
        y="Count",
        title="Customer Segment Distribution"
    )

    fig_segment.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_segment,
        use_container_width=True,
        key="segment_chart"
    )

with right:

    fig_revenue = px.bar(
    category_data,
    x="product_category_name_english",
    y="price",
    title="Top Revenue Categories"
)
    
    fig_revenue.update_layout(
    height=450,
    xaxis_title="Category",
    yaxis_title="Revenue"
)
    fig_revenue.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
        key="revenue_chart"
    )


st.markdown("---")

fig_state = px.bar(
    sales_state,
    x="customer_state",
    y="payment_value",
    title="Revenue by State",
    text_auto=".2s"
)

fig_state.update_layout(
    height=500,
    xaxis_title="State",
    yaxis_title="Revenue"
)

st.plotly_chart(
    fig_state,
    use_container_width=True,
    key="revenue_by_state"
)
# --------------------------------------------------
# BUSINESS INSIGHTS
# --------------------------------------------------

st.markdown("---")

st.subheader("📌 Key Business Insights")

if category_data.empty:

    st.warning(
        "No data available for the selected filters."
    )

else:

    top_category = category_data.iloc[0][
        "product_category_name_english"
    ]

    top_revenue = category_data.iloc[0][
        "price"
    ]

    st.info(f"""
• Highest revenue category: {top_category}

• Revenue generated: ${top_revenue:,.0f}

• Average Order Value: ${aov:.2f}

• Total Customers: {total_customers:,}

• Late Deliveries: {late_percentage:.2f}%
""")