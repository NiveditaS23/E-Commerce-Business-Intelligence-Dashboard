import streamlit as st
import pandas as pd
import plotly.express as px

from pathlib import Path

st.set_page_config(
    page_title="Customer Intelligence",
    page_icon="👥",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parents[2]

rfm_segments = pd.read_csv(
    BASE_DIR / "data/processed/rfm_segments.csv"
)

st.title("👥 Customer Intelligence")

# Calculate first
champions = (
    rfm_segments["Segment"] == "Champions"
).sum()

at_risk = (
    rfm_segments["Segment"] == "At Risk"
).sum()

loyal = (
    rfm_segments["Segment"] == "Loyal Customers"
).sum()

potential = (
    rfm_segments["Segment"] == "Potential Loyalists"
).sum()

st.markdown("---")

# Then display
col1, col2, col3, col4 = st.columns(4)

col1.metric("Champions", f"{champions:,}")
col2.metric("At Risk", f"{at_risk:,}")
col3.metric("Loyal Customers", f"{loyal:,}")
col4.metric("Potential Loyalists", f"{potential:,}")

segment_counts = (
    rfm_segments["Segment"]
    .value_counts()
    .reset_index()
)

segment_counts.columns = [
    "Segment",
    "Count"
]

fig_segment = px.bar(
    segment_counts,
    x="Segment",
    y="Count",
    title="Customer Segment Distribution"
)




col1, col2, col3 = st.columns(3)

with col1:

    fig_recency = px.histogram(
        rfm_segments,
        x="Recency",
        title="Recency Distribution"
    )

    st.plotly_chart(
        fig_recency,
        use_container_width=True,
        key="recency_hist"
    )



with col2:

    fig_frequency = px.histogram(
        rfm_segments,
        x="Frequency",
        title="Frequency Distribution"
    )

    st.plotly_chart(
        fig_frequency,
        use_container_width=True,
        key="frequency_hist"
    )



with col3:

    fig_monetary = px.histogram(
        rfm_segments,
        x="Monetary",
        title="Monetary Distribution"
    )

    st.plotly_chart(
        fig_monetary,
        use_container_width=True,
        key="monetary_hist"
    )


    st.markdown("---")

fig_pie = px.pie(
    segment_counts,
    names="Segment",
    values="Count",
    title="Customer Segment Share"
)



left, right = st.columns(2)

with left:
    st.plotly_chart(
        fig_segment,
        use_container_width=True,
        key="segment_distribution"
    )

with right:
    st.plotly_chart(
        fig_pie,
        use_container_width=True,
        key="segment_pie"
    )

for chart in [
    fig_segment,
    fig_pie,
    fig_recency,
    fig_frequency,
    fig_monetary
]:
    chart.update_layout(
        template="plotly_white"
    )


st.markdown("---")

st.subheader("📌 Customer Insights")
st.info("""
• 24,081 customers are At Risk.

• Retention campaigns should target At Risk customers.

• Champions represent the highest-value customers.

• Loyalty programs should focus on Loyal Customers and Champions.

• Potential Loyalists can be converted through targeted promotions.
""")


