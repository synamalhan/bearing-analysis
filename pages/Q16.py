import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q16: Bearing Make vs Lifespan")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q16: How does bearing make influence lifespan in identical operating conditions?")
st.markdown("Compare bearing brands under similar speeds (RPM), machine types, and bearing sizes.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()

# Clean & engineer columns
df = df.dropna(subset=["subscription_start", "timestamp_of_fault", "rpm_min", "rpm_max", "bearing_make"])
df["lifespan_days"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days
df["avg_rpm"] = (df["rpm_min"] + df["rpm_max"]) / 2

# -- FILTERS --

# RPM Range Filter
rpm_range = st.slider("Filter by RPM", 
                      min_value=int(df["avg_rpm"].min()), 
                      max_value=int(df["avg_rpm"].max()), 
                      value=(int(df["avg_rpm"].min()), int(df["avg_rpm"].max())))

# Machine Type Filter (if column exists)
if "machine_type" in df.columns:
    machine_types = df["machine_type"].dropna().unique().tolist()
    selected_machine = st.selectbox("Select Machine Type", ["All"] + machine_types)
else:
    selected_machine = "All"

# Bearing Size Filter (if column exists)
if "bearing_size" in df.columns:
    bearing_sizes = df["bearing_size"].dropna().unique().tolist()
    selected_sizes = st.multiselect("Select Bearing Sizes", options=bearing_sizes, default=bearing_sizes)
else:
    selected_sizes = []

# Lifespan Filter
lifespan_range = st.slider("Filter by Lifespan (days)",
                           min_value=int(df["lifespan_days"].min()),
                           max_value=int(df["lifespan_days"].max()),
                           value=(int(df["lifespan_days"].min()), int(df["lifespan_days"].max())))

# -- APPLY FILTERS --
filtered_df = df[df["avg_rpm"].between(rpm_range[0], rpm_range[1])]
filtered_df = filtered_df[filtered_df["lifespan_days"].between(lifespan_range[0], lifespan_range[1])]

if selected_machine != "All":
    filtered_df = filtered_df[filtered_df["machine_type"] == selected_machine]

if selected_sizes:
    filtered_df = filtered_df[filtered_df["bearing_size"].isin(selected_sizes)]

# -- PLOT --
st.subheader("Lifespan Comparison by Bearing Make")
fig = px.box(
    filtered_df,
    x="bearing_make",
    y="lifespan_days",
    color="bearing_make",
    points="all",
    title="Lifespan by Bearing Brand (Filtered)",
    labels={"lifespan_days": "Lifespan (days)", "bearing_make": "Bearing Brand"}
)
st.plotly_chart(fig, use_container_width=True)
