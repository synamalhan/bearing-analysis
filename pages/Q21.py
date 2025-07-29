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

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df = df[df["timestamp_of_fault"].notna() & df["subscription_start"].notna()]
    df = df[df["bearing_severity_class"].isin([1, 2])]

    df["rpm_bucket"] = pd.cut(df["rpm_max"], bins=[0, 1000, 3000, 6000, 10000], labels=["Low", "Medium", "High", "Very High"])
    df["bearing_key"] = df["bearing_type_assigned_1"].astype(str) + "|" + \
                        df["bearing_make"].astype(str) + "|" + \
                        df["industry_type"].astype(str) + "|" + \
                        df["monitor_id"].astype(str)

    class1 = df[df["bearing_severity_class"] == 1][["bearing_key", "subscription_start"]].copy()
    class2 = df[df["bearing_severity_class"] == 2].copy()

    merged = pd.merge_asof(
        class2.sort_values("timestamp_of_fault"),
        class1.sort_values("subscription_start"),
        by="bearing_key",
        left_on="timestamp_of_fault",
        right_on="subscription_start",
        direction="backward",
        allow_exact_matches=True
    )

    def determine_lubrication(row):
        if pd.notna(row["subscription_start_y"]) and str(row["lubrication_type"]).strip().lower() != "not available":
            return "With Lubrication"
        else:
            return "Without Lubrication"

    merged["lubrication_condition"] = merged.apply(determine_lubrication, axis=1)
    merged["time_to_failure_days"] = (merged["timestamp_of_fault"] - merged["subscription_start_y"].fillna(merged["subscription_start_x"])).dt.days

    merged.rename(columns={
        "subscription_start_x": "subscription_start",
        "subscription_start_y": "lubricated_from_subscription"
    }, inplace=True)

    return merged

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
df_filtered = filter_with_all(df_filtered, "lubrication_condition", selected_lube)
df_filtered = filter_with_all(df_filtered, "designation_brg", selected_designation)

if df_filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --- Chart 1: Lubrication Impact ---
st.markdown("### Lubrication Impact on Failure Timing")
lube_chart = df_filtered.groupby("lubrication_condition")["time_to_failure_days"].agg(["count", "median"]).reset_index()
lube_chart.rename(columns={"count": "Failure Count", "median": "Median Days"}, inplace=True)

fig = px.bar(
    lube_chart,
    x="lubrication_condition",
    y="Median Days",
    color="lubrication_condition",
    text="Failure Count",
    title="Median Time to Failure: With vs. Without Lubrication",
    labels={"lubrication_condition": "Lubrication Condition", "Median Days": "Median Time to Failure (days)"}
)
st.plotly_chart(fig, use_container_width=True)

# --- Expanders ---
st.markdown("### Detailed Records by Lubrication Condition")

with_lube_df = df_filtered[df_filtered["lubrication_condition"] == "With Lubrication"]
without_lube_df = df_filtered[df_filtered["lubrication_condition"] == "Without Lubrication"]

with st.expander("With Lubrication Entries"):
    st.write("Entries where lubrication was recorded before the failure.")
    st.dataframe(
        with_lube_df[[
            "monitor_id", "bearing_make", "bearing_type_assigned_1", "designation_brg", "industry_type",
            "rpm_bucket", "lubrication_type", "lubricated_from_subscription",
            "timestamp_of_fault", "time_to_failure_days"
        ]].sort_values("timestamp_of_fault")
    )

with st.expander("Without Lubrication Entries"):
    st.write("Entries with no recorded lubrication before failure.")
    st.dataframe(
        without_lube_df[[
            "monitor_id", "bearing_make", "bearing_type_assigned_1", "designation_brg", "industry_type",
            "rpm_bucket", "lubrication_type", "timestamp_of_fault", "time_to_failure_days"
        ]].sort_values("timestamp_of_fault")
    )

# --- Chart 2: Boxplot by Lubrication Type ---
st.markdown("### Time to Failure Distribution by Lubrication Type")
box_fig = px.box(
    df_filtered,
    x="lubrication_type",
    y="time_to_failure_days",
    color="lubrication_type",
    title="Distribution of Time to Failure by Lubrication Type",
    labels={"time_to_failure_days": "Time to Failure (Days)", "lubrication_type": "Lubrication"},
)
st.plotly_chart(box_fig, use_container_width=True)

# --- Chart 3: Median by Lubrication and Bearing Make ---
st.markdown("### Median Time to Failure by Lubrication and Bearing Make")
median_by_make_lube = df_filtered.groupby(["lubrication_type", "bearing_make"])["time_to_failure_days"].median().reset_index()

bar_fig = px.bar(
    median_by_make_lube,
    x="bearing_make",
    y="time_to_failure_days",
    color="lubrication_type",
    barmode="group",
    title="Median Time to Failure Grouped by Lubrication and Make",
    labels={"time_to_failure_days": "Median Time to Failure (Days)", "bearing_make": "Bearing Make"},
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- Chart 4: Faceted by Industry and RPM ---
st.markdown("### Faceted Median Failure Time by Industry, RPM, and Lubrication")
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

# --- Binary Decision Tree: Industry → Machine Type → Lubrication Condition ---
st.markdown("## Binary Rule Tree: Lubrication Interval by Machine Type")

# Filter only valid entries
tree_df = df_filtered.copy()
tree_df = tree_df[~tree_df["machine_type"].isna() & ~tree_df["industry_type"].isna()]

# Only keep groups with at least 5 samples
valid_groups = tree_df.groupby(["industry_type", "machine_type"]).filter(lambda x: len(x) >= 5)

# Get sorted industries and divide into chunks of 3
industries = sorted(valid_groups["industry_type"].unique())
industry_chunks = [industries[i:i+3] for i in range(0, len(industries), 3)]

for chunk in industry_chunks:
    cols = st.columns(len(chunk))  # Create 1 to 3 columns depending on chunk size
    
    for idx, industry in enumerate(chunk):
        with cols[idx]:
            st.markdown(f"### Industry: `{industry}`")
            industry_df = valid_groups[valid_groups["industry_type"] == industry]
            machines = sorted(industry_df["machine_type"].unique())

            for machine in machines:
                machine_df = industry_df[industry_df["machine_type"] == machine]
                n = len(machine_df)

                st.markdown(f"#### Machine: `{machine}` (n={n})")

                # Lubrication = Without
                no_lube = machine_df[machine_df["lubrication_condition"] == "Without Lubrication"]
                yes_lube = machine_df[machine_df["lubrication_condition"] == "With Lubrication"]

                # Branch 1: Without Lubrication
                if len(no_lube) >= 1:
                    median_days = int(no_lube["time_to_failure_days"].median())
                    st.markdown(f"- **Without Lubrication** (n={len(no_lube)}): Lubricate every **≤ {median_days} days** ⏳")
                else:
                    st.markdown(f"- **Without Lubrication**: _Insufficient data_")

                # Branch 2: With Lubrication
                if len(yes_lube) >= 1:
                    median_yes = int(yes_lube["time_to_failure_days"].median())
                    st.markdown(f"- **With Lubrication** (n={len(yes_lube)}): Failures occur after ~**{median_yes} days** 🛡️")
                else:
                    st.markdown(f"- **With Lubrication**: _Insufficient data_")
