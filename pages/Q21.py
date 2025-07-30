import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q21: Bearing Failure Timing by Designation", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q21: Bearing Failure Timing Analysis by Designation")

st.markdown("""
This analysis explores **time to failure** for *bearing clearance issues* (`bearing_severity_class == 2`), segmented by:

- Industry type
- RPM bucket
- Bearing make
- Bearing type
- Bearing designation
- Lubrication condition (including **absence of lubrication**)
""")
import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    # Load Excel
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=[
        "subscription_start", "timestamp_of_fault"
    ])
    
    # Only keep relevant severity classes
    df = df[df["bearing_severity_class"].isin([1, 2, 3])]
    df = df.dropna(subset=["timestamp_of_fault", "subscription_start", "monitor_id"])
    df = df.sort_values(by=["monitor_id", "timestamp_of_fault"])

    # Step 1: Compute 'bearing_available_since' using class 3 resets
    bearing_available_since_list = []

    for monitor_id, group in df.groupby("monitor_id"):
        last_class_3_time = None

        for _, row in group.iterrows():
            if row["bearing_severity_class"] == 3:
                last_class_3_time = row["timestamp_of_fault"]
                bearing_available_since_list.append(None)  # We'll drop class 3 rows later
            else:
                available_since = last_class_3_time or row["subscription_start"]
                bearing_available_since_list.append(available_since)

    df["bearing_available_since"] = bearing_available_since_list

    # Drop class 3 rows (used only to determine reset point)
    df = df[df["bearing_severity_class"].isin([1, 2])].copy()

    

    for monitor_id, group in df.groupby("monitor_id"):
        class_1_rows = group[group["bearing_severity_class"] == 1]
        class_2_rows = group[group["bearing_severity_class"] == 2]

        for idx, row in class_2_rows.iterrows():
            available_since = row["bearing_available_since"]
            fault_time = row["timestamp_of_fault"]

            # Check if any class 1 issue occurred in between
            intervening = class_1_rows[
                (class_1_rows["timestamp_of_fault"] > available_since) &
                (class_1_rows["timestamp_of_fault"] < fault_time)
            ]

            if len(intervening) > 0:
                df.loc[idx, "lubricated_from_subscription"] = "With Lubrication"
            else:
                df.loc[idx, "lubricated_from_subscription"] = "Without Lubrication"

    # Step 3: Create RPM bucket column
    if "rpm_min" in df.columns and "rpm_max" in df.columns:
        df["rpm_bucket"] = df["rpm_min"].astype(str) + " to " + df["rpm_max"].astype(str)
    else:
        df["rpm_bucket"] = "Unknown"
    
    df["time_to_failure_days"] = (df["timestamp_of_fault"] - df["bearing_available_since"]).dt.days


    return df


df = load_data()

# --- Filters layout ---
col1, col2, col3, col4, col5, col6 = st.columns(6)

all_industries = ["All"] + sorted(df["industry_type"].dropna().unique())
all_rpms = ["All"] + df["rpm_bucket"].dropna().unique().tolist()
all_makes = ["All"] + sorted(df["bearing_make"].dropna().unique())
all_types = ["All"] + sorted(df["bearing_type_assigned_1"].dropna().unique())
all_lubes = ["All"] + ["With Lubrication", "Without Lubrication"]
all_designations = ["All"] + sorted(df["designation_brg"].dropna().unique())

with col1:
    selected_industry = st.multiselect("Industry", all_industries, default=["All"])
with col2:
    selected_rpm = st.multiselect("RPM Bucket", all_rpms, default=["All"])
with col3:
    selected_make = st.multiselect("Bearing Make", all_makes, default=["All"])
with col4:
    selected_type = st.multiselect("Bearing Type", all_types, default=["All"])
with col5:
    selected_lube = st.multiselect("Lubrication", all_lubes, default=["All"])
with col6:
    selected_designation = st.multiselect("Bearing Designation", all_designations, default=["All"])

def filter_with_all(df, column, selected_values):
    if "All" in selected_values or not selected_values:
        return df
    return df[df[column].isin(selected_values)]

df_filtered = df.copy()
df_filtered = filter_with_all(df_filtered, "industry_type", selected_industry)
df_filtered = filter_with_all(df_filtered, "rpm_bucket", selected_rpm)
df_filtered = filter_with_all(df_filtered, "bearing_make", selected_make)
df_filtered = filter_with_all(df_filtered, "bearing_type_assigned_1", selected_type)
df_filtered = filter_with_all(df_filtered, "lubricated_from_subscription", selected_lube)
df_filtered = filter_with_all(df_filtered, "designation_brg", selected_designation)

if df_filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --- Chart 1 ---
st.markdown("### Lubrication Impact on Failure Timing")
lube_chart = df_filtered.groupby("lubricated_from_subscription")["time_to_failure_days"].agg(["count", "median"]).reset_index()
lube_chart.rename(columns={"count": "Failure Count", "median": "Median Days"}, inplace=True)

fig = px.bar(
    lube_chart,
    x="lubricated_from_subscription",
    y="Median Days",
    color="lubricated_from_subscription",
    text="Failure Count",
    title="Median Time to Failure: With vs. Without Lubrication",
)
st.plotly_chart(fig, use_container_width=True)

# --- Expanders ---
st.markdown("### Detailed Records by Lubrication Condition")

with_lube_df = df_filtered[df_filtered["lubricated_from_subscription"] == "With Lubrication"]
without_lube_df = df_filtered[df_filtered["lubricated_from_subscription"] == "Without Lubrication"]

with st.expander("With Lubrication Entries"):
    st.write("Entries where lubrication was recorded before the failure.")
    st.dataframe(
        with_lube_df[[
            "monitor_id", "bearing_make", "bearing_type_assigned_1", "designation_brg", "industry_type",
            "rpm_bucket", "Lubrication Method",
            "timestamp_of_fault", "time_to_failure_days", "bearing_available_since"
        ]].sort_values("timestamp_of_fault")
    )

with st.expander("Without Lubrication Entries"):
    st.write("Entries with no recorded lubrication before failure.")
    st.dataframe(
        without_lube_df[[
            "monitor_id", "bearing_make", "bearing_type_assigned_1", "designation_brg", "industry_type",
            "rpm_bucket", "Lubrication Method",
            "timestamp_of_fault", "time_to_failure_days", "bearing_available_since"
        ]].sort_values("timestamp_of_fault")
    )

# --- Boxplot by Lubrication Method ---
st.markdown("### Time to Failure Distribution by Lubrication Type")
box_fig = px.box(
    df_filtered,
    x="Lubrication Method",
    y="time_to_failure_days",
    color="Lubrication Method",
    title="Distribution of Time to Failure by Lubrication Type",
    labels={"time_to_failure_days": "Time to Failure (Days)"},
)
st.plotly_chart(box_fig, use_container_width=True)

# --- Median by Lubrication and Make ---
st.markdown("### Median Time to Failure by Lubrication and Bearing Make")
median_by_make_lube = df_filtered.groupby(["Lubrication Method", "bearing_make"])["time_to_failure_days"].median().reset_index()

bar_fig = px.bar(
    median_by_make_lube,
    x="bearing_make",
    y="time_to_failure_days",
    color="Lubrication Method",
    barmode="group",
    title="Median Time to Failure Grouped by Lubrication and Make",
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- Faceted box by Industry ---
st.markdown("### Faceted Median Failure Time by Industry, RPM, and Lubrication")
facet_fig = px.box(
    df_filtered,
    x="rpm_bucket",
    y="time_to_failure_days",
    color="Lubrication Method",
    facet_col="industry_type",
    title="Failure Time across RPM and Industry (Faceted by Industry)",
)
st.plotly_chart(facet_fig, use_container_width=True)

import streamlit as st
import pandas as pd
import tempfile
from pyvis.network import Network

# Assuming `df_filtered` is your prepared dataframe
df = df_filtered.copy()
df = df.dropna(subset=["industry_type", "asset_type", "lubricated_from_subscription", "time_to_failure_days"])

# Only include "With Lubrication" entries
df = df[df["lubricated_from_subscription"].str.lower().str.contains("with")]

# Create Pyvis network
net = Network(height="650px", width="100%", bgcolor="#222", font_color="white", directed=True)

net.set_options("""
{
  "layout": {
    "hierarchical": {
      "enabled": true,
      "direction": "LR",
      "sortMethod": "directed"
    }
  },
  "nodes": {
    "shape": "dot",
    "size": 20,
    "font": {
      "size": 14,
      "face": "Tahoma"
    }
  },
  "edges": {
    "width": 2,
    "color": {
      "inherit": true
    },
    "smooth": {
      "type": "continuous"
    }
  },
  "physics": {
    "enabled": true,
    "hierarchicalRepulsion": {
      "nodeDistance": 140
    }
  },
  "interaction": {
    "dragNodes": true,
    "hover": true,
    "tooltipDelay": 200
  }
}
""")

# Track added nodes
seen = set()
valid_group_count = 0

# Loop through grouped data
for (industry, machine, lube_status), group in df.groupby(["industry_type", "asset_type", "lubricated_from_subscription"]):
    if group.shape[0] <= 4:
        continue  # Skip groups with less than 3 samples

    valid_group_count += 1
    median_days = int(group["time_to_failure_days"].median())
    lube_label = f"Recommended to lubricate after ~{median_days} days"

    # Add industry node
    if industry not in seen:
        net.add_node(industry, label=industry, level=0)
        seen.add(industry)

    # Add machine node
    machine_node = f"{industry}_{machine}"
    if machine_node not in seen:
        net.add_node(machine_node, label=machine, level=1)
        net.add_edge(industry, machine_node)
        seen.add(machine_node)

    # Add lubrication node
    lube_node = f"{machine_node}_{lube_status}"
    if lube_node not in seen:
        net.add_node(lube_node, label=lube_label, level=2, color="#2ca02c")
        net.add_edge(machine_node, lube_node)
        seen.add(lube_node)

# Handle case when all groups were filtered out
if valid_group_count == 0:
    st.warning("No lubrication groups with at least 3 records found.")
    st.stop()

# Save and display the graph
with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".html") as f:
    net.save_graph(f.name)
    html_content = open(f.name, "r").read()

st.markdown("### 🧠 Lubrication Recommendation Tree")
st.components.v1.html(html_content, height=700, scrolling=True)

# Updated Summary Table
st.markdown("### 📋 Lubrication Recommendations Summary")

summary = (
    df.groupby(["industry_type", "asset_type"])
    .filter(lambda x: len(x) >= 4)
    .groupby(["industry_type", "asset_type"])
    .agg(
        recommended_days=("time_to_failure_days", lambda x: int(x.median())),
        samples=("time_to_failure_days", "count")
    )
    .reset_index()
)

summary = summary.rename(columns={
    "industry_type": "Industry",
    "asset_type": "Machine",
    "recommended_days": "Recommended Lubrication Cycle (days)",
    "samples": "Data Points"
})

st.dataframe(summary, use_container_width=True)
