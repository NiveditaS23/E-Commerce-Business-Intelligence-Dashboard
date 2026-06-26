import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# --------------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------------

st.set_page_config(
    page_title="Executive Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Executive Business Dashboard")

# --------------------------------------------------------
# LOAD DATA
# --------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

@st.cache_data
def load_data():

    orders = pd.read_csv(
        BASE_DIR / "data/raw/olist_orders_dataset.csv"
    )

    payments = pd.read_csv(
        BASE_DIR / "data/raw/olist_order_payments_dataset.csv"
    )

    customers = pd.read_csv(
        BASE_DIR / "data/raw/olist_customers_dataset.csv"
    )

    items = pd.read_csv(
        BASE_DIR / "data/raw/olist_order_items_dataset.csv"
    )

    products = pd.read_csv(
        BASE_DIR / "data/raw/olist_products_dataset.csv"
    )

    category_translation = pd.read_csv(
        BASE_DIR /
        "data/raw/product_category_name_translation.csv"
    )

    return (
        orders,
        payments,
        customers,
        items,
        products,
        category_translation
    )

(
    orders,
    payments,
    customers,
    items,
    products,
    category_translation
) = load_data()

# --------------------------------------------------------
# DATA PREPARATION
# --------------------------------------------------------

sales = (
    orders
    .merge(
        payments,
        on="order_id",
        how="left"
    )
    .merge(
        customers,
        on="customer_id",
        how="left"
    )
)

sales["order_purchase_timestamp"] = pd.to_datetime(
    sales["order_purchase_timestamp"]
)

sales["Year"] = (
    sales["order_purchase_timestamp"]
    .dt.year
)

sales["Month"] = (
    sales["order_purchase_timestamp"]
    .dt.strftime("%b")
)

sales["Month_Number"] = (
    sales["order_purchase_timestamp"]
    .dt.month
)

sales["YearMonth"] = (
    sales["order_purchase_timestamp"]
    .dt.to_period("M")
)

# --------------------------------------------------------
# PRODUCT MERGE
# --------------------------------------------------------

product_sales = (
    items
    .merge(
        products,
        on="product_id",
        how="left"
    )
    .merge(
        category_translation,
        on="product_category_name",
        how="left"
    )
    .merge(
        payments,
        on="order_id",
        how="left"
    )
)

product_sales[
    "product_category_name_english"
] = product_sales[
    "product_category_name_english"
].fillna("Unknown")

# --------------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------------

st.sidebar.header("Dashboard Filters")

years = sorted(
    sales["Year"].unique()
)

selected_year = st.sidebar.selectbox(
    "Select Year",
    ["All"] + years
)

states = sorted(
    sales["customer_state"]
    .dropna()
    .unique()
)

selected_state = st.sidebar.selectbox(
    "Select State",
    ["All"] + list(states)
)

status = sorted(
    sales["order_status"]
    .dropna()
    .unique()
)

selected_status = st.sidebar.selectbox(
    "Order Status",
    ["All"] + list(status)
)

# --------------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------------

filtered_sales = sales.copy()

if selected_year != "All":

    filtered_sales = filtered_sales[
        filtered_sales["Year"] == selected_year
    ]

if selected_state != "All":

    filtered_sales = filtered_sales[
        filtered_sales["customer_state"]
        == selected_state
    ]

if selected_status != "All":

    filtered_sales = filtered_sales[
        filtered_sales["order_status"]
        == selected_status
    ]

if filtered_sales.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()

if filtered_sales.empty:

    st.warning(
        "No data available for the selected filters. Please choose different filter values."
    )

    st.stop()

# --------------------------------------------------------
# MONTHLY DATA
# --------------------------------------------------------

monthly = (
    filtered_sales
    .groupby("YearMonth")
    .agg(
        Revenue=("payment_value", "sum"),
        Orders=("order_id", "nunique")
    )
    .reset_index()
)

if monthly.empty:
    st.warning(
        "No data available for the selected filters. Please choose different filter values."
    )
    st.stop()

monthly["YearMonth"] = monthly[
    "YearMonth"
].astype(str)

monthly["YearMonth"] = pd.to_datetime(
    monthly["YearMonth"]
)

monthly["Average Order Value"] = (
    monthly["Revenue"]
    /
    monthly["Orders"]
)



# --------------------------------------------------------
# KPI CALCULATIONS
# ------------------------------------------# --------------------------------------------------------
# COMMON CHART STYLE
# --------------------------------------------------------

def style_chart(fig):

    fig.update_layout(
        template="plotly_white",
        height=430,
        title_x=0.02,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),
        font=dict(
            size=13
        )
    )

    return fig

total_revenue = (
    filtered_sales["payment_value"]
    .sum()
)

total_orders = (
    filtered_sales["order_id"]
    .nunique()
)

average_order_value = (
    total_revenue
    /
    total_orders
)

states_served = (
    filtered_sales["customer_state"]
    .nunique()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "📦 Total Orders",
    f"{total_orders:,}"
)

col3.metric(
    "🛒 Average Order Value",
    f"${average_order_value:,.2f}"
)

col4.metric(
    "🌍 States Served",
    states_served
)

st.markdown("---")

# --------------------------------------------------------
# MONTHLY REVENUE TREND
# --------------------------------------------------------

fig_revenue = px.line(
    monthly,
    x="YearMonth",
    y="Revenue",
    markers=True,
    color_discrete_sequence=["#1F77B4"],
    title="Monthly Revenue Trend"
)

fig_revenue.update_traces(
    line=dict(width=3)
)

fig_revenue = style_chart(fig_revenue)

fig_revenue.update_yaxes(
    tickprefix="$"
)

# --------------------------------------------------------
# MONTHLY ORDERS
# --------------------------------------------------------

fig_orders = px.bar(
    monthly,
    x="YearMonth",
    y="Orders",
    title="Monthly Orders",
    color_discrete_sequence=["#5DADE2"]
)

fig_orders = style_chart(fig_orders)

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_revenue,
        use_container_width=True,
        key="monthly_revenue"
    )

with right:

    st.plotly_chart(
        fig_orders,
        use_container_width=True,
        key="monthly_orders"
    )

# --------------------------------------------------------
# REVENUE BY STATE
# --------------------------------------------------------

state_revenue = (
    filtered_sales
    .groupby("customer_state")["payment_value"]
    .sum()
    .reset_index()
    .sort_values(
        "payment_value",
        ascending=False
    )
)

top_states = state_revenue.head(10)

fig_states = px.bar(
    top_states,
    x="payment_value",
    y="customer_state",
    orientation="h",
    title="Top 10 States by Revenue",
    color="payment_value",
    color_continuous_scale="Blues"
)

fig_states = style_chart(fig_states)

fig_states.update_xaxes(
    tickprefix="$"
)

# --------------------------------------------------------
# TOP PRODUCT CATEGORIES
# --------------------------------------------------------

valid_orders = filtered_sales[
    "order_id"
].unique()

category_revenue = (
    product_sales[
        product_sales["order_id"].isin(valid_orders)
    ]
    .groupby(
        "product_category_name_english"
    )["payment_value"]
    .sum()
    .reset_index()
    .sort_values(
        "payment_value",
        ascending=False
    )
    .head(10)
)

fig_categories = px.bar(
    category_revenue,
    x="payment_value",
    y="product_category_name_english",
    orientation="h",
    title="Top Product Categories by Revenue",
    color="payment_value",
    color_continuous_scale="Blues"
)

fig_categories = style_chart(fig_categories)

fig_categories.update_xaxes(
    tickprefix="$"
)

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_states,
        use_container_width=True,
        key="state_revenue"
    )

with right:

    st.plotly_chart(
        fig_categories,
        use_container_width=True,
        key="category_revenue"
    )

    # --------------------------------------------------------
# AVERAGE ORDER VALUE TREND
# --------------------------------------------------------

fig_aov = px.line(
    monthly,
    x="YearMonth",
    y="Average Order Value",
    markers=True,
    color_discrete_sequence=["#2E86C1"],
    title="Average Order Value Trend"
)

fig_aov.update_traces(
    line=dict(width=3)
)

fig_aov = style_chart(fig_aov)

fig_aov.update_yaxes(
    tickprefix="$"
)

# --------------------------------------------------------
# ORDER STATUS DISTRIBUTION
# --------------------------------------------------------

status_summary = (
    filtered_sales
    .groupby("order_status")
    .agg(
        Revenue=("payment_value", "sum"),
        Orders=("order_id", "nunique")
    )
    .reset_index()
)

fig_status = px.pie(
    status_summary,
    names="order_status",
    values="Revenue",
    hole=0.55,
    color_discrete_sequence=px.colors.sequential.Blues,
    title="Revenue Distribution by Order Status"
)

fig_status = style_chart(fig_status)

left, right = st.columns(2)

with left:

    st.plotly_chart(
        fig_aov,
        use_container_width=True,
        key="aov_trend"
    )

with right:

    st.plotly_chart(
        fig_status,
        use_container_width=True,
        key="status_distribution"
    )

st.markdown("---")

# --------------------------------------------------------
# MONTHLY PERFORMANCE TABLE
# --------------------------------------------------------

performance = monthly.copy()

performance["Revenue"] = (
    performance["Revenue"]
    .round(2)
)

performance["Average Order Value"] = (
    performance["Average Order Value"]
    .round(2)
)

performance.rename(
    columns={
        "YearMonth":"Month"
    },
    inplace=True
)

st.subheader("📅 Monthly Business Performance")

st.dataframe(
    performance,
    use_container_width=True,
    hide_index=True
)

st.markdown("---")

# --------------------------------------------------------
# BUSINESS HIGHLIGHTS
# --------------------------------------------------------

highest_month = monthly.loc[
    monthly["Revenue"].idxmax()
]

lowest_month = monthly.loc[
    monthly["Revenue"].idxmin()
]

if state_revenue.empty:

    top_state = "No Data"
    top_state_revenue = 0

else:

    top_state = (
        state_revenue.iloc[0]["customer_state"]
    )

    top_state_revenue = (
        state_revenue.iloc[0]["payment_value"]
    )

top_state_revenue = (
    state_revenue
    .iloc[0]["payment_value"]
)

if category_revenue.empty:

    top_category = "No Data"
    top_category_revenue = 0

else:

    top_category = (
        category_revenue.iloc[0]["product_category_name_english"]
    )

    top_category_revenue = (
        category_revenue.iloc[0]["payment_value"]
    )

highest_orders = (
    monthly["Orders"].max()
)

average_monthly_revenue = (
    monthly["Revenue"].mean()
)

average_monthly_orders = (
    monthly["Orders"].mean()
)

# --------------------------------------------------------
# EXECUTIVE SUMMARY
# --------------------------------------------------------

st.subheader("📌 Executive Summary")

growth = 0

if len(monthly) > 1:

    growth = (
        (
            monthly["Revenue"].iloc[-1]
            -
            monthly["Revenue"].iloc[-2]
        )
        /
        monthly["Revenue"].iloc[-2]
    ) * 100

growth_color = "🟢" if growth >= 0 else "🔴"

with st.container(border=True):

    st.subheader("Executive Summary")

    st.write(
        f"**Total Revenue:** ${total_revenue:,.0f}"
    )

    st.write(
        f"**Total Orders:** {total_orders:,}"
    )

    st.write(
        f"**Average Order Value:** ${average_order_value:,.2f}"
    )

    st.write(
        f"**Highest Revenue Month:** {highest_month['YearMonth'].strftime('%B %Y')}"
    )

    st.write(
        f"**Highest Revenue State:** {top_state}"
    )

    st.write(
        f"**Best Performing Category:** {top_category}"
    )

st.markdown("---")

# --------------------------------------------------------
# MANAGEMENT RECOMMENDATIONS
# --------------------------------------------------------

st.subheader("💼 Strategic Recommendations")

recommendations = []

if growth > 5:
    recommendations.append(
        "Revenue is growing steadily. Consider expanding inventory to support increasing demand."
    )
else:
    recommendations.append(
        "Revenue growth is slowing. Consider promotional campaigns or seasonal offers."
    )

recommendations.append(
    f"Prioritize marketing investment in **{top_state}**, the highest revenue generating state."
)

recommendations.append(
    f"Increase stock availability for **{top_category}**, currently the highest earning product category."
)

recommendations.append(
    "Monitor Average Order Value and introduce bundle offers to improve customer spending."
)

recommendations.append(
    "Review states with low revenue to identify expansion opportunities."
)

for i, rec in enumerate(recommendations, start=1):
    st.write(f"**{i}.** {rec}")

st.markdown("---")
