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
- Bearing type
- Bearing make
- Lubrication condition (including **absence of lubrication**)

""")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df = df[df["bearing_severity_class"] == 2]
    df = df[df["timestamp_of_fault"].notna() & df["subscription_start"].notna()]
    df["time_to_failure_days"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days
    df = df[df["time_to_failure_days"] > 0]  # Remove invalid durations
    df["rpm_bucket"] = pd.cut(df["rpm_max"], bins=[0, 1000, 3000, 6000, 10000], labels=["Low", "Medium", "High", "Very High"])

    # Normalize lubrication labels
    df["lubrication_condition"] = df["lubrication_type"].fillna("Unknown").apply(lambda x: "Without Lubrication" if x.strip().lower() in ["not available", "none", "na", "unknown"] else "With Lubrication")
    
    return df

df = load_data()

if df.empty:
    st.warning("No bearing clearance records with valid timestamps found.")
    st.stop()

# --- Sidebar Filters ---
col1, col2, col3, col4, col5 = st.columns(5)

industry_options = sorted(df["industry_type"].dropna().unique())
rpm_options = df["rpm_bucket"].dropna().unique()
type_options = sorted(df["bearing_type_assigned_1"].dropna().unique())
make_options = sorted(df["bearing_make"].dropna().unique())
lube_conditions = ["With Lubrication", "Without Lubrication"]

with col1:
    selected_industries = st.multiselect("Industry", industry_options, default=industry_options)
with col2:
    selected_rpms = st.multiselect("RPM Bucket", list(rpm_options), default=list(rpm_options))
with col3:
    selected_types = st.multiselect("Bearing Type", type_options, default=type_options)
with col4:
    selected_makes = st.multiselect("Bearing Make", make_options, default=make_options)
with col5:
    selected_lubes = st.multiselect("Lubrication Condition", lube_conditions, default=lube_conditions)

# --- Filtered Dataset ---
df_filtered = df[
    (df["industry_type"].isin(selected_industries)) &
    (df["rpm_bucket"].isin(selected_rpms)) &
    (df["bearing_type_assigned_1"].isin(selected_types)) &
    (df["bearing_make"].isin(selected_makes)) &
    (df["lubrication_condition"].isin(selected_lubes))
]

if df_filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# # --- Summary Table ---
# summary = df_filtered.groupby(
#     ["industry_type", "rpm_bucket", "bearing_type_assigned_1", "bearing_make", "lubrication_condition"]
# )["time_to_failure_days"].agg(["count", "mean", "median"]).reset_index()

# summary.columns = ["Industry", "RPM", "Bearing Type", "Make", "Lubrication", "Failures", "Mean Days", "Median Days"]
# st.markdown("### Failure Timing Summary for Bearing Clearance")
# st.dataframe(summary, use_container_width=True)

# --- Lubrication Comparison Chart ---
st.markdown("### Lubrication Impact on Failure Timing")

lube_chart = df_filtered.groupby("lubrication_condition")["time_to_failure_days"].agg(["count", "mean", "median"]).reset_index()
lube_chart.rename(columns={"count": "Failure Count", "mean": "Mean Days", "median": "Median Days"}, inplace=True)

fig = px.bar(
    lube_chart,
    x="lubrication_condition",
    y="Mean Days",
    color="lubrication_condition",
    title="Average Time to Failure: With vs. Without Lubrication",
    text="Failure Count",
    labels={"lubrication_condition": "Lubrication Condition", "Mean Days": "Avg. Time to Failure (days)"}
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Time to Failure Distribution by Lubrication Condition")
box_fig = px.box(
    df_filtered,
    x="lubrication_type",
    y="time_to_failure_days",
    color="lubrication_type",
    title="Distribution of Time to Failure by Lubrication Type",
    labels={"time_to_failure_days": "Time to Failure (Days)", "lubrication_type": "Lubrication"},
)
st.plotly_chart(box_fig, use_container_width=True)

# Mean Failure Time by Lubrication + Bearing Make
st.markdown("### Mean Time to Failure by Lubrication and Bearing Make")
bar_fig = px.bar(
    df_filtered.groupby(["lubrication_type", "bearing_make"])["time_to_failure_days"].mean().reset_index(),
    x="bearing_make",
    y="time_to_failure_days",
    color="lubrication_type",
    barmode="group",
    title="Mean Time to Failure Grouped by Lubrication and Make",
    labels={"time_to_failure_days": "Mean Time to Failure (Days)", "bearing_make": "Bearing Make"},
)
st.plotly_chart(bar_fig, use_container_width=True)

# Optional: Industry + Lubrication + RPM
st.markdown("### Faceted Time to Failure by Industry, RPM, and Lubrication")
facet_fig = px.box(
    df_filtered,
    x="rpm_bucket",
    y="time_to_failure_days",
    color="lubrication_type",
    facet_col="industry_type",
    title="Failure Time across RPM and Industry (Faceted by Industry)",
    labels={"time_to_failure_days": "Failure Time (Days)", "rpm_bucket": "RPM Bucket"},
)
st.plotly_chart(facet_fig, use_container_width=True)
