import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q19: Bearing Clearance Timing", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q19: When Do Bearing Clearance Issues Occur?")
st.markdown("""
This analysis investigates the **time to failure** for *bearing clearance issues* (`bearing_severity_class == 2`), segmented across:

- Industry type
- RPM bucket
- Lubrication method
- Bearing designation
- Bearing make
""")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df = df[df["bearing_severity_class"] == 2]
    df = df[df["timestamp_of_fault"].notna() & df["subscription_start"].notna()]
    df["time_to_failure_days"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days
    df = df[df["time_to_failure_days"] > 0]

    df["rpm_bucket"] = pd.cut(df["rpm_max"], bins=[0, 1000, 3000, 6000, 10000], labels=["Low", "Medium", "High", "Very High"])
    df["lubrication_method"] = df["lubrication_type"].fillna("Unknown").apply(lambda x: x.strip().title())
    df["designation_brg"] = df["designation_brg"].fillna("Unknown").astype(str)
    
    return df

df = load_data()

# --- Filters ---
st.subheader("Filter Parameters")

col1, col2, col3, col4 = st.columns(4)

with col1:
    industry_options = ["All"] + sorted(df["industry_type"].dropna().unique().tolist())
    selected_industry = st.selectbox("Industry Type", industry_options)

with col2:
    machine_options = ["All"] + sorted(df["machine_type"].dropna().unique().tolist())
    selected_machine = st.selectbox("Machine Type", machine_options)

with col3:
    lube_options = ["All"] + sorted(df["lubrication_method"].dropna().unique().tolist())
    selected_lube = st.selectbox("Lubrication Method", lube_options)

with col4:
    rpm_options = ["All"] + list(df["rpm_bucket"].dropna().unique())
    selected_rpm = st.selectbox("RPM Bucket", rpm_options)

col5, col6 = st.columns([1, 2])
with col5:
    selected_designation = st.selectbox("Fix Bearing Designation", sorted(df["designation_brg"].dropna().unique()))

# --- Apply filters ---
df_filtered = df[
    (df["designation_brg"] == selected_designation) &
    (df["industry_type"].isin([selected_industry]) if selected_industry != "All" else True) &
    (df["machine_type"].isin([selected_machine]) if selected_machine != "All" else True) &
    (df["lubrication_method"].isin([selected_lube]) if selected_lube != "All" else True) &
    (df["rpm_bucket"].isin([selected_rpm]) if selected_rpm != "All" else True)
]

if df_filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --- Summary Table ---
summary = df_filtered.groupby("bearing_make")["time_to_failure_days"].agg(["count", "mean", "median"]).reset_index()
summary.columns = ["Bearing Make", "Failure Count", "Mean Time to Failure (Days)", "Median Time to Failure (Days)"]
summary = summary[summary["Failure Count"] > 0]

st.markdown("### 📋 Summary Table: Bearing Makes (within selected designation)")
st.dataframe(summary.sort_values("Mean Time to Failure (Days)", ascending=False), use_container_width=True)

# --- Plot ---
st.markdown("### 📊 Time to Failure by Bearing Make")

fig = px.bar(
    summary,
    x="Bearing Make",
    y="Mean Time to Failure (Days)",
    text="Failure Count",
    color="Bearing Make",
    title=f"Average Time to Failure for Bearing Makes (Designation: {selected_designation})",
)
fig.update_layout(showlegend=False)
st.plotly_chart(fig, use_container_width=True)
