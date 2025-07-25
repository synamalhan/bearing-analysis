import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q19: Bearing Clearance Timing", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q19: When Do Bearing Clearance Issues Occur?")
st.markdown("This analysis explores the expected time of failure for **bearing clearance** issues, segmented by RPM, bearing make/type, industry, and lubrication presence.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "timestamp_of_installation"])
    df = df[df["issue_type"] == "Bearing Clearance"]
    df["time_to_failure_days"] = (df["timestamp_of_fault"] - df["timestamp_of_installation"]).dt.days
    df["rpm_bucket"] = pd.cut(df["rpm"], bins=[0, 1000, 3000, 6000, 10000], labels=["Low", "Medium", "High", "Very High"])
    return df

df = load_data()

# --- Filters ---
col1, col2, col3, col4, col5 = st.columns(5)

industry_options = sorted(df["industry_type"].dropna().unique().tolist())
rpm_options = df["rpm_bucket"].dropna().unique().tolist()
bearing_type_options = sorted(df["bearing_type"].dropna().unique().tolist())
bearing_make_options = sorted(df["bearing_make"].dropna().unique().tolist())
lube_options = sorted(df["lubrication_type"].dropna().unique().tolist())

with col1:
    selected_industries = st.multiselect("Industry Type", ["All"] + industry_options, default=["All"])
with col2:
    selected_rpms = st.multiselect("RPM Bucket", ["All"] + list(rpm_options), default=["All"])
with col3:
    selected_types = st.multiselect("Bearing Type", ["All"] + bearing_type_options, default=["All"])
with col4:
    selected_makes = st.multiselect("Bearing Make", ["All"] + bearing_make_options, default=["All"])
with col5:
    selected_lubes = st.multiselect("Lubrication Type", ["All"] + lube_options, default=["All"])

# --- Apply filters ---
if "All" not in selected_industries:
    df = df[df["industry_type"].isin(selected_industries)]
if "All" not in selected_rpms:
    df = df[df["rpm_bucket"].isin(selected_rpms)]
if "All" not in selected_types:
    df = df[df["bearing_type"].isin(selected_types)]
if "All" not in selected_makes:
    df = df[df["bearing_make"].isin(selected_makes)]
if "All" not in selected_lubes:
    df = df[df["lubrication_type"].isin(selected_lubes)]

# --- Summary Table ---
grouped = df.groupby(["industry_type", "rpm_bucket", "bearing_type", "bearing_make", "lubrication_type"])["time_to_failure_days"].agg(["count", "mean", "median"]).reset_index()
grouped.rename(columns={"count": "Failure Count", "mean": "Mean Days", "median": "Median Days"}, inplace=True)

st.markdown("### Summary: Expected Failure Timing for Bearing Clearance Issues")
st.dataframe(grouped, use_container_width=True)

# ---
