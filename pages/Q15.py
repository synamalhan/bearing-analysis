# Q9.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q15: Failure Distribution by RPM & Machine Type")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q15: What is the distribution of failures by RPM and machine type?")
st.markdown("Visualize where failure density is highest.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault"])
    return df

df = load_data()

# Drop rows with missing values required for this analysis
df = df.dropna(subset=["rpm_min", "rpm_max", "machine_type", "timestamp_of_fault"])

# Calculate average RPM
df["avg_rpm"] = (df["rpm_min"] + df["rpm_max"]) / 2

# Filters
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        selected_machines = st.multiselect("Filter by Machine Type", options=sorted(df["machine_type"].unique()), default=df["machine_type"].unique())
    with col2:
        rpm_range = st.slider("Filter by RPM", min_value=int(df["avg_rpm"].min()), max_value=int(df["avg_rpm"].max()), value=(int(df["avg_rpm"].min()), int(df["avg_rpm"].max())))

# Apply filters
filtered_df = df[
    (df["machine_type"].isin(selected_machines)) &
    (df["avg_rpm"].between(rpm_range[0], rpm_range[1]))
]

# Density heatmap
st.subheader("Failure Density by RPM and Machine Type")
fig = px.density_heatmap(
    filtered_df,
    x="avg_rpm",
    y="machine_type",
    nbinsx=40,
    title="Failure Heatmap: RPM vs Machine Type",
    labels={"avg_rpm": "Average RPM", "machine_type": "Machine Type"},
    color_continuous_scale="Reds"
)
st.plotly_chart(fig, use_container_width=True)
