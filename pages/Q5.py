import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q4: Lubrication vs Failure Timing")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q4: Lubrication Timing vs Failure Timing")
st.markdown("""
Analyze how soon bearings fail after a lubrication event.
""")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault"])
    return df

df = load_data()
df.columns = df.columns.str.strip().str.lower()



# Keep severity 1, 2, 3 only
df = df[df["bearing_severity_class"].isin([1, 2, 3])]

# Step 2: For easier analysis, group by monitor_id and sort by timestamp
df_sorted = df.sort_values(["monitor_id", "timestamp_of_fault"])

results = []

for monitor_id, group in df_sorted.groupby("monitor_id"):
    group = group.reset_index(drop=True)

    lube_dates = group[group["bearing_severity_class"].isin([1, 2])]["timestamp_of_fault"].tolist()
    fail_dates = group[group["bearing_severity_class"].isin([2, 3])]["timestamp_of_fault"].tolist()

    if lube_dates and fail_dates:
        # Assume last lube before failure
        for fail_date in fail_dates:
            lube_before_fail = [d for d in lube_dates if d < fail_date]
            if lube_before_fail:
                last_lube = max(lube_before_fail)
                days_between = (fail_date - last_lube).days
                results.append({
                    "monitor_id": monitor_id,
                    "last_lube": last_lube,
                    "fail_date": fail_date,
                    "days_between": days_between,
                    "industry_type": group["industry_type"].iloc[0],
                    "bearing_make": group["bearing_make"].iloc[0],
                    "bearing_type": group[["bearing_type_assigned_1", "bearing_type_assigned_2", "bearing_type_assigned_3"]].bfill(axis=1).iloc[0,0],
                    "machine_type": group["machine_type"].iloc[0],
                    "rpm": group["rpm_min"].iloc[0]
                })

# Convert to DataFrame
case_df = pd.DataFrame(results)
# --- Filters ---
industries = st.multiselect("Industry Type", options=["All"] + sorted(case_df["industry_type"].unique().tolist()), default="All")
if "All" not in industries:
    case_df = case_df[case_df["industry_type"].isin(industries)]

st.metric("Total Cases", len(case_df))
st.metric("Average Days Between Lubrication and Failure", round(case_df["days_between"].mean(), 2))

# --- Table ---
st.subheader("Lubrication to Failure Details")
st.dataframe(case_df.sort_values("days_between", ascending=False), use_container_width=True)

# --- Plot ---
st.subheader("Time Between Lubrication and Failure")
fig = px.histogram(case_df, x="days_between", nbins=20, title="Distribution of Days Between Lubrication and Failure")
st.plotly_chart(fig, use_container_width=True)
