import streamlit as st
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Q11: Bearing Make vs Failure Severity", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q11. Are certain bearing makes associated with consistently higher or lower severity failures?")
st.markdown("🔍 Link brand reliability with severity trends to guide procurement decisions.")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()

# --- Optional Filters ---
with st.expander("Optional Filters"):
    industry = st.selectbox("Filter by Industry", ["All"] + sorted(df["industry_type"].dropna().unique()))
    machine = st.selectbox("Filter by Machine Type", ["All"] + sorted(df["machine_type"].dropna().unique()))
    rpm_range = st.selectbox("Filter by RPM Range", ["All", "Low (<1000)", "Medium (1000-3000)", "High (>3000)"])

    if industry != "All":
        df = df[df["industry_type"] == industry]
    if machine != "All":
        df = df[df["machine_type"] == machine]
    if rpm_range != "All":
        if rpm_range == "Low (<1000)":
            df = df[df["rpm"] < 1000]
        elif rpm_range == "Medium (1000-3000)":
            df = df[(df["rpm"] >= 1000) & (df["rpm"] <= 3000)]
        else:
            df = df[df["rpm"] > 3000]

# --- Bar Plot ---
if "bearing_make" in df.columns and "bearing_severity_class" in df.columns:
    severity_by_make = df.groupby(["bearing_make", "bearing_severity_class"]).size().reset_index(name="count")

    fig = px.bar(
        severity_by_make,
        x="bearing_make",
        y="count",
        color="bearing_severity_class",
        barmode="group",
        title="Failure Severity Distribution by Bearing Make",
        labels={
            "bearing_make": "Bearing Make",
            "count": "Failure Count",
            "bearing_severity_class": "Severity Class"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Severity Share Table ---
    st.subheader("Percentage Breakdown of Failures by Severity (per Bearing Make)")
    pivot = severity_by_make.pivot(index="bearing_make", columns="bearing_severity_class", values="count").fillna(0)
    percent_table = (pivot.T / pivot.sum(axis=1)).T * 100
    st.dataframe(percent_table.round(2))
else:
    st.error("Required columns `bearing_make` or `bearing_severity_class` not found in the dataset.")
