import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler

# --- Config ---
st.set_page_config(page_title="Q2: Bearing Across Assets", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.markdown("### Q2: Within a fixed industry, how do the same bearing types perform across different asset types?")
st.markdown("You can analyze how a **single bearing type** behaves across different machine types, bearing makes, and RPMs within the selected industry. This helps assess asset-specific suitability.")
st.divider()

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df['operational_days'] = (df['timestamp_of_fault'] - df['subscription_start']).dt.days

    def rpm_bucket(rpm):
        if pd.isna(rpm):
            return "Unknown"
        elif rpm < 200:
            return "(0-200)"
        elif rpm < 900:
            return "(200-900)"
        elif rpm < 1500:
            return "(900-1500)"
        else:
            return "(1500+)"

    df['rpm_range'] = df['rpm_min'].apply(rpm_bucket)
    df['asset_type'] = df['machine_type'] + " | " + df['bearing_make']
    return df.dropna(subset=['operational_days'])

df = load_data()

# --- Layout ---
left, right = st.columns([1, 2])

with left:
    st.subheader("Filters")

    # --- Industry filter ---
    industry_list = sorted(df['industry_type'].dropna().unique())
    selected_industry = st.selectbox("Industry", industry_list)
    df_filtered = df[df['industry_type'] == selected_industry]

    # --- Bearing Type (Multiselect with All) ---
    bearing_list = sorted(df_filtered['bearing_type_assigned_1'].dropna().unique())
    selected_bearings = st.multiselect("Bearing Types", options=["All"] + bearing_list, default=["All"])
    if "All" in selected_bearings:
        selected_bearings = bearing_list

    # --- Machine Type (Multiselect with All) ---
    machines = sorted(df_filtered['machine_type'].dropna().unique())
    selected_machines = st.multiselect("Machine Types", options=["All"] + machines, default=["All"])
    if "All" in selected_machines:
        selected_machines = machines

    # --- Bearing Make (Multiselect with All) ---
    makes = sorted(df_filtered['bearing_make'].dropna().unique())
    selected_makes = st.multiselect("Bearing Makes", options=["All"] + makes, default=["All"])
    if "All" in selected_makes:
        selected_makes = makes

    # --- RPM Ranges (Multiselect with All) ---
    rpms = sorted(df_filtered['rpm_range'].dropna().unique())
    selected_rpms = st.multiselect("RPM Ranges", options=["All"] + rpms, default=["All"])
    if "All" in selected_rpms:
        selected_rpms = rpms

    show_table = st.toggle("Show Summary Table", value=False)

with right:
    st.subheader(f"Performance of {', '.join(selected_bearings)} in {selected_industry}")

    # --- Final Filtering ---
    plot_df = df_filtered[
        (df_filtered['bearing_type_assigned_1'].isin(selected_bearings)) &
        (df_filtered['machine_type'].isin(selected_machines)) &
        (df_filtered['bearing_make'].isin(selected_makes)) &
        (df_filtered['rpm_range'].isin(selected_rpms))
    ]

    if plot_df.empty:
        st.warning("No matching data found.")
    else:
        # --- Box Plot ---
        fig = px.box(
            plot_df,
            x='asset_type',
            y='operational_days',
            color='rpm_range',
            points='all',
            title=f"Lifespan of Bearings Across Asset Types",
            labels={'asset_type': 'Asset (Machine + Make)', 'operational_days': 'Operational Days'},
        )
        fig.update_layout(xaxis_tickangle=-30, height=500)
        st.plotly_chart(fig, use_container_width=True)

        if show_table:
            stats = plot_df.groupby(['asset_type', 'rpm_range'])['operational_days'].agg(
                count='count',
                mean='mean',
                median='median',
                std='std'
            ).reset_index()

            st.markdown("### Summary Table")
            st.dataframe(stats.rename(columns={
                'mean': 'Avg Days',
                'median': 'Median',
                'std': 'Std Dev',
                'count': 'Sample Count'
            }), use_container_width=True)
