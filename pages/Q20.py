import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------
# Page Title & Intro
# -------------------
st.title("Q20. How does bearing make affect average bearing life across different conditions?")
st.markdown("""
Analyze how various **bearing makes** perform in terms of **average life**, filtered by:
- Industry Type
- Machine Type
- Lubrication Method
- RPM Bucket
- Bearing Severity Class

The analysis is done **per designation**, which you can select below.  
Use filters to refine the scope and see comparisons.
""")

# -------------------
# Load and Preprocess
# -------------------
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx")

    # Clean and compute life
    df = df.dropna(subset=["bearing_make", "designation_brg", "timestamp_of_fault", "subscription_start"])
    df["subscription_start"] = pd.to_datetime(df["subscription_start"])
    df["timestamp_of_fault"] = pd.to_datetime(df["timestamp_of_fault"])
    df["avg_bearing_life"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.total_seconds() / (3600 * 24)

    # RPM Bucket
    df["rpm_bucket"] = pd.cut(
        df["rpm_max"],
        bins=[0, 1000, 3000, 6000, 10000],
        labels=["Low", "Medium", "High", "Very High"]
    )
    return df

df = load_data()

# -------------------
# Helper: Multiselect with All
# -------------------
def multiselect_with_all_body(label, column):
    options = sorted(df[column].dropna().unique())
    all_opts = ["All"] + options
    selected = st.multiselect(label, all_opts, default=["All"])
    return options if "All" in selected or not selected else selected

# -------------------
# Filters (Main Area)
# -------------------
st.markdown("### Filter Parameters")

col1, col2 = st.columns(2)
with col1:
    industry_filter = multiselect_with_all_body("Industry Type", "industry_type")
    machine_filter  = multiselect_with_all_body("Machine Type", "machine_type")
    lube_filter     = multiselect_with_all_body("Lubrication Method", "lubrication_type")
with col2:
    rpm_filter      = multiselect_with_all_body("RPM Bucket", "rpm_bucket")
    severity_filter = multiselect_with_all_body("Bearing Severity Class", "bearing_severity_class")

# -------------------
# Designation Selector
# -------------------
selected_designation = st.selectbox("Select a Designation to Compare Makes", sorted(df["designation_brg"].dropna().unique()))

# -------------------
# Filter Data
# -------------------
df_filtered = df[
    (df["designation_brg"] == selected_designation) &
    (df["industry_type"].isin(industry_filter)) &
    (df["machine_type"].isin(machine_filter)) &
    (df["lubrication_type"].isin(lube_filter)) &
    (df["rpm_bucket"].isin(rpm_filter)) &
    (df["bearing_severity_class"].isin(severity_filter))
]

if df_filtered.empty:
    st.warning(" No data available for the selected filters and designation.")
else:
    # -------------------
    # Summary Table
    # -------------------
    summary_df = df_filtered.groupby("bearing_make")["avg_bearing_life"].agg(["mean", "median", "count"]).reset_index()
    summary_df = summary_df[summary_df["count"] > 0]
    summary_df = summary_df.rename(columns={
        "bearing_make": "Bearing Make",
        "mean": "Mean Life (days)",
        "median": "Median Life (days)",
        "count": "Number of Records"
    })

    # -------------------
    # Bar Plot
    # -------------------
    st.subheader(f"Average Bearing Life by Make (Designation: {selected_designation})")
    plt.figure(figsize=(10, 5))
    sns.barplot(data=summary_df.sort_values("Mean Life (days)", ascending=False),
                x="Bearing Make", y="Mean Life (days)", palette="Set2")
    plt.xticks(rotation=45)
    plt.title("Mean Bearing Life per Make")
    st.pyplot(plt)

    # -------------------
    # Summary Table
    # -------------------
    st.markdown("### Summary Table")
    st.dataframe(summary_df.style.format({"Mean Life (days)": "{:.1f}", "Median Life (days)": "{:.1f}"}), use_container_width=True)

    
# -------------------
# Pivot Table: Unique Makes per Designation
# -------------------
st.markdown("### Unique Bearing Make Count per Designation")
pivot_counts = (
    df.groupby("designation_brg")["bearing_make"]
    .nunique()
    .reset_index()
    .rename(columns={"bearing_make": "Number of Unique Makes"})
)
st.dataframe(pivot_counts.style.highlight_max(axis=0), use_container_width=True)
