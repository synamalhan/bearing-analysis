import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Q13: Time-to-Failure by Machine Type", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q13. What is the median time-to-failure from subscription start across different machine types?")
st.markdown("📆 Assess asset lifespan to schedule preventive replacements accurately.")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()

# Filter valid rows
df = df.dropna(subset=["subscription_start", "timestamp_of_fault", "machine_type"])
df["time_to_failure_days"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days

# Optional filters
with st.expander("🔧 Optional Filters"):
    industry = st.selectbox("Filter by Industry", ["All"] + sorted(df["industry_type"].dropna().unique()))
    bearing_make = st.selectbox("Filter by Bearing Make", ["All"] + sorted(df["bearing_make"].dropna().unique()))

    if industry != "All":
        df = df[df["industry_type"] == industry]
    if bearing_make != "All":
        df = df[df["bearing_make"] == bearing_make]

# Median time-to-failure by machine type
median_df = df.groupby("machine_type")["time_to_failure_days"].median().reset_index()
median_df = median_df.sort_values("time_to_failure_days", ascending=False)

# Plot
fig = px.bar(
    median_df,
    x="machine_type",
    y="time_to_failure_days",
    title="Median Time-to-Failure from Subscription Start (by Machine Type)",
    labels={"machine_type": "Machine Type", "time_to_failure_days": "Median Days to Failure"},
    color="time_to_failure_days",
    color_continuous_scale="Blues"
)

st.plotly_chart(fig, use_container_width=True)

# Show table
st.subheader("📋 Median Days to Failure per Machine Type")
st.dataframe(median_df.set_index("machine_type").style.format("{:.0f}"))
