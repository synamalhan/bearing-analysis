import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q4: Bearing Type vs Lifespan")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)

st.title("Q4: Do certain bearing types consistently fail earlier than others across different RPM ranges?")
st.markdown("Identify early-failing bearings under low, medium, and high RPM conditions.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()

# Drop missing and compute lifespan + average RPM
df = df.dropna(subset=["subscription_start", "timestamp_of_fault", "rpm_min", "rpm_max", "bearing_type_assigned_1"])
df["lifespan_days"] = (df["timestamp_of_fault"] - df["subscription_start"]).dt.days
df["avg_rpm"] = (df["rpm_min"] + df["rpm_max"]) / 2

# RPM bins: Low (<1000), Medium (1000–3000), High (>3000)
def rpm_category(rpm):
    if rpm < 1000:
        return "Low"
    elif rpm <= 3000:
        return "Medium"
    else:
        return "High"

df["rpm_category"] = df["avg_rpm"].apply(rpm_category)

# --- RPM Category Filter ---
rpm_category = st.selectbox("Select RPM Range", options=["All", "Low", "Medium", "High"])

# --- Bearing Type Filter ---
bearing_types = ["All"] + sorted(df["bearing_type_assigned_1"].dropna().unique().tolist())
selected_bearing = st.selectbox("Filter by Bearing Type", bearing_types)

# --- Industry Filter ---
industry_types = ["All"] + sorted(df["industry_type"].dropna().unique().tolist())
selected_industry = st.selectbox("Filter by Industry", industry_types)

# --- Machine Type Filter ---
machine_types = ["All"] + sorted(df["machine_type"].dropna().unique().tolist())
selected_machine = st.selectbox("Filter by Machine Type", machine_types)

# --- Filtering Logic ---
filtered_df = df.copy()

if rpm_category != "All":
    filtered_df = filtered_df[filtered_df["rpm_category"] == rpm_category]

if selected_bearing != "All":
    filtered_df = filtered_df[filtered_df["bearing_type_assigned_1"] == selected_bearing]

if selected_industry != "All":
    filtered_df = filtered_df[filtered_df["industry_type"] == selected_industry]

if selected_machine != "All":
    filtered_df = filtered_df[filtered_df["machine_type"] == selected_machine]

# --- Plot ---
if filtered_df.empty:
    st.warning("No data available for selected filters.")
else:
    fig = px.box(
        filtered_df,
        x="bearing_type_assigned_1",
        y="lifespan_days",
        color="bearing_type_assigned_1",
        points="all",
        labels={
            "lifespan_days": "Lifespan (days)",
            "bearing_type_assigned_1": "Bearing Type"
        },
        title=f"Lifespan by Bearing Type{' - ' + rpm_category if rpm_category != 'All' else ''}"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Optional: Count table
    st.subheader("Failure Count by Bearing Type")
    count_df = filtered_df["bearing_type_assigned_1"].value_counts().reset_index()
    count_df.columns = ["Bearing Type", "Count"]
    st.dataframe(count_df)
