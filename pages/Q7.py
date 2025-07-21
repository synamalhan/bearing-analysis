import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
st.set_page_config(page_title="Q7: Missing Lubrication vs Severity", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q7. Is there any association between missing lubrication data and higher severity failures?")
st.markdown("Investigate if 'Not Available' lubrication records correlate with increased risk.")
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()
# --- Preprocessing ---
df["lubrication_status"] = df["lubrication_type"]
df["is_lubrication_missing"] = df["lubrication_status"].str.lower().str.contains("not available")

# Optional filters
with st.expander("Optional Filters"):
    industry = st.selectbox("Filter by Industry", ["All"] + sorted(df["industry_type"].dropna().unique().tolist()))
    machine = st.selectbox("Filter by Machine Type", ["All"] + sorted(df["machine_type"].dropna().unique().tolist()))

    if industry != "All":
        df = df[df["industry_type"] == industry]
    if machine != "All":
        df = df[df["machine_type"] == machine]

# --- Bar plot: Severity vs Missing Lubrication ---
if "bearing_severity_class" in df.columns:
    severity_counts = df.groupby(["is_lubrication_missing", "bearing_severity_class"]).size().reset_index(name="count")
    
    fig = px.bar(
        severity_counts,
        x="bearing_severity_class",
        y="count",
        color="is_lubrication_missing",
        barmode="group",
        labels={
            "is_lubrication_missing": "Lubrication Missing",
            "bearing_severity_class": "Failure Severity",
            "count": "Count"
        },
        title="Failure Severity Distribution vs. Lubrication Availability"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Percent breakdown
    st.subheader(" Severity Breakdown (Percent with Missing Lubrication)")
    total = severity_counts.groupby("bearing_severity_class")["count"].sum()
    missing = severity_counts[severity_counts["is_lubrication_missing"] == True].set_index("bearing_severity_class")["count"]
    percent_missing = (missing / total * 100).fillna(0).round(2)
    st.dataframe(percent_missing.reset_index().rename(columns={"count": "% Failures with Missing Lubrication"}))

else:
    st.error(" Column `bearing_severity_class` not found in the dataset.")
