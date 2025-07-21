import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Q8: Preventive Replacement Interval")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q8: What is the ideal preventive replacement interval?")
st.markdown("Estimate data-driven preventive maintenance thresholds (median / 75th percentile).")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start", "subscription_end"])
    return df

df = load_data()

# Only rows with valid start and failure timestamps
df = df.dropna(subset=["subscription_start", "timestamp_of_fault"])
df["days_to_failure"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days
df = df[df["days_to_failure"] > 0]

# ─────────────────────────────
# Page Layout: 2 columns
# ─────────────────────────────
left_col, right_col = st.columns([1, 2])

with left_col:
    st.markdown("### 🔧 Filter Options")

    filter_cols = ["bearing_make", "bearing_type_assigned_1", "machine_type", "industry_type", "lubrication_type"]

    for col in filter_cols:
        if col in df.columns:
            options = df[col].dropna().unique().tolist()
            selected = st.multiselect(f"{col.replace('_', ' ').title()}", options, default=options, key=col)
            df = df[df[col].isin(selected)]

with right_col:
    if df.empty:
        st.warning("⚠️ No data available after applying filters.")
    else:
        median_days = int(df["days_to_failure"].median())
        percentile_75 = int(np.percentile(df["days_to_failure"], 75))

        st.metric("Median Failure Interval", f"{median_days} days")
        st.metric("75th Percentile Failure Interval", f"{percentile_75} days")

        # Histogram
        st.subheader("Distribution of Days to Failure")
        fig = px.histogram(df, x="days_to_failure", nbins=50, title="Histogram of Days to Failure")
        st.plotly_chart(fig, use_container_width=True)

        # Boxplot
        st.subheader("Boxplot of Days to Failure by Bearing Type")
        fig2 = px.box(df, x="bearing_type_assigned_1", y="days_to_failure", title="Failure Interval by Bearing Type")
        st.plotly_chart(fig2, use_container_width=True)
