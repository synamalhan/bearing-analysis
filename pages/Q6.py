import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q6: Lubrication Impact on Failure", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q6: Does Lubrication Prolong Bearing Life?")
st.markdown("This analysis checks if prior lubrication is associated with lower failure probability and longer bearing life.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault"])
    df = df[df["bearing_severity_class"].isin([1, 2, 3])]
    return df

df = load_data()

# --- Filters in columns ---
col1, col2, col3, col4 = st.columns(4)

# Get unique values
bearing_options = sorted(df["bearing_make"].dropna().unique().tolist())
industry_options = sorted(df["industry_type"].dropna().unique().tolist())
machine_options = sorted(df["machine_type"].dropna().unique().tolist())
lube_options = sorted(df["lubrication_type"].dropna().unique().tolist())

with col1:
    selected_bearings = st.multiselect("Bearing Make", ["All"] + bearing_options, default=["All"])
with col2:
    selected_industries = st.multiselect("Industry Type", ["All"] + industry_options, default=["All"])
with col3:
    selected_machines = st.multiselect("Machine Type", ["All"] + machine_options, default=["All"])
with col4:
    selected_lubes = st.multiselect("Lubrication Method", ["All"] + lube_options, default=["All"])

# --- Apply filters ---
if "All" not in selected_bearings:
    df = df[df["bearing_make"].isin(selected_bearings)]
if "All" not in selected_industries:
    df = df[df["industry_type"].isin(selected_industries)]
if "All" not in selected_machines:
    df = df[df["machine_type"].isin(selected_machines)]
if "All" not in selected_lubes:
    df = df[df["lubrication_type"].isin(selected_lubes)]

# --- Analyze: Time since last lubrication vs failure ---
df_sorted = df.sort_values(["monitor_id", "timestamp_of_fault"])
results = []

for monitor_id, group in df_sorted.groupby("monitor_id"):
    group = group.reset_index(drop=True)
    lube_events = group[group["bearing_severity_class"] == 1]["timestamp_of_fault"].tolist()  # Assume severity 1 = lubrication
    fail_events = group[group["bearing_severity_class"].isin([2, 3])]["timestamp_of_fault"].tolist()

    for fail_date in fail_events:
        lube_before = [d for d in lube_events if d < fail_date]
        if lube_before:
            last_lube = max(lube_before)
            days_between = (fail_date - last_lube).days
            results.append({
                "monitor_id": monitor_id,
                "lubed_before_fail": True,
                "days_between": days_between,
                "fail_date": fail_date
            })
        else:
            results.append({
                "monitor_id": monitor_id,
                "lubed_before_fail": False,
                "days_between": None,
                "fail_date": fail_date
            })

case_df = pd.DataFrame(results)

# --- Summary Metrics ---
total_failures = len(case_df)
lubed_failures = case_df["lubed_before_fail"].sum()
not_lubed_failures = total_failures - lubed_failures

col1, col2, col3 = st.columns(3)
col1.metric("Total Failures", total_failures)
col2.metric("Lubricated Before Failure", lubed_failures)
col3.metric("Not Lubricated Before Failure", not_lubed_failures)

st.markdown("### Failure Probability")
st.write(f"**Failure with Lubrication**: {round(100 * lubed_failures / total_failures, 2)}%")
st.write(f"**Failure without Lubrication**: {round(100 * not_lubed_failures / total_failures, 2)}%")

# --- Average days between lube and failure ---
avg_days = case_df[case_df["lubed_before_fail"] == True]["days_between"].mean()
st.markdown(f"### Avg. Days Between Last Lube and Failure: `{round(avg_days, 1)} days`")

# --- Plot: Lubed vs Not Lubed Failure Count ---
count_plot = case_df["lubed_before_fail"].value_counts().reset_index()
count_plot.columns = ["Lubricated Before Failure", "Count"]
count_plot["Lubricated Before Failure"] = count_plot["Lubricated Before Failure"].map({True: "Yes", False: "No"})

fig = px.bar(count_plot, x="Lubricated Before Failure", y="Count", color="Lubricated Before Failure",
             title="Failure Count by Lubrication History", color_discrete_map={"Yes": "#4CAF50", "No": "#F44336"})
st.plotly_chart(fig, use_container_width=True)

# --- Optional: Table of all cases ---
with st.expander("View Raw Failure Records"):
    st.dataframe(case_df.drop(columns=["fail_date"]), use_container_width=True)
