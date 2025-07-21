import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q6: Lubrication Pattern Insights")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q6: Lubrication Patterns by Group")
st.markdown("Visualize how lubrication timing relates to failure across groups.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault"])
    return df

df = load_data()

# Pre-process like Q4
df = df[df["bearing_severity_class"].isin([1, 2, 3])]
df_sorted = df.sort_values(["monitor_id", "timestamp_of_fault"])

results = []

for monitor_id, group in df_sorted.groupby("monitor_id"):
    group = group.reset_index(drop=True)
    lube_dates = group[group["bearing_severity_class"].isin([1, 2])]["timestamp_of_fault"].tolist()
    fail_dates = group[group["bearing_severity_class"].isin([2, 3])]["timestamp_of_fault"].tolist()

    if lube_dates and fail_dates:
        for fail_date in fail_dates:
            lube_before_fail = [d for d in lube_dates if d < fail_date]
            if lube_before_fail:
                last_lube = max(lube_before_fail)
                days_between = (fail_date - last_lube).days
                results.append({
                    "monitor_id": monitor_id,
                    "group_key": f"{group['industry_type'].iloc[0]} | {group['bearing_make'].iloc[0]} | {group['machine_type'].iloc[0]} | {group['rpm_min'].iloc[0]}",
                    "days_between": days_between
                })

case_df = pd.DataFrame(results)

# --- Group-level Aggregation ---
group_stats = case_df.groupby("group_key")["days_between"].agg(["mean", "median", "count"]).reset_index()
group_stats = group_stats[group_stats["count"] >= 2]  # Only show groups with enough data

st.metric("Total Groups", len(group_stats))
st.metric("Overall Avg Days Between Lube and Failure", round(case_df["days_between"].mean(), 1))

# --- Table ---
st.subheader("Group-level Lubrication Insights")
st.dataframe(group_stats.sort_values("mean", ascending=False), use_container_width=True)

# --- Plot ---
st.subheader("Group Comparison")
fig = px.bar(group_stats, x="group_key", y="mean", title="Average Days Between Lube and Failure by Group", labels={"mean": "Avg Days"}, height=600)
st.plotly_chart(fig, use_container_width=True)
