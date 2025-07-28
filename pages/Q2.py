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

    industry_list = sorted(df['industry_type'].dropna().unique())
    selected_industry = st.selectbox("Industry", industry_list)
    df_filtered = df[df['industry_type'] == selected_industry]

    bearing_list = sorted(df_filtered['bearing_type_assigned_1'].dropna().unique())
    selected_bearing = st.selectbox("Bearing Type", bearing_list)

    machines = sorted(df_filtered['machine_type'].dropna().unique())
    selected_machines = st.multiselect("Machine Types", options=["All"] + machines, default=["All"])
    if "All" in selected_machines:
        selected_machines = machines

    makes = sorted(df_filtered['bearing_make'].dropna().unique())
    selected_makes = st.multiselect("Bearing Makes", options=["All"] + makes, default=["All"])
    if "All" in selected_makes:
        selected_makes = makes

    rpms = sorted(df_filtered['rpm_range'].dropna().unique())
    selected_rpms = st.multiselect("RPM Ranges", options=["All"] + rpms, default=["All"])
    if "All" in selected_rpms:
        selected_rpms = rpms

    show_table = st.toggle("Show Summary Table", value=False)

with right:
    st.subheader(f"Performance of '{selected_bearing}' in {selected_industry}")

    # --- Final Filtering ---
    plot_df = df_filtered[
        (df_filtered['bearing_type_assigned_1'] == selected_bearing) &
        (df_filtered['machine_type'].isin(selected_machines)) &
        (df_filtered['bearing_make'].isin(selected_makes)) &
        (df_filtered['rpm_range'].isin(selected_rpms))
    ]

    if plot_df.empty:
        st.warning("No matching data found.")
    else:
        # --- Box Plot (Main) ---
        fig = px.box(
            plot_df,
            x='asset_type',
            y='operational_days',
            color='rpm_range',
            points='all',
            title=f"Lifespan of Bearing '{selected_bearing}' Across Asset Types",
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

        st.divider()
        st.subheader("Additional Visualizations")

        # --- 1. Faceted Box Plot (All Bearings in Industry) ---
        st.markdown("#### Box Plot Faceted by Bearing Type")
        top_bearings = (
            df_filtered['bearing_type_assigned_1'].value_counts()
            .head(6)
            .index.tolist()
        )

        faceted = df_filtered[
            (df_filtered['machine_type'].isin(selected_machines)) &
            (df_filtered['bearing_make'].isin(selected_makes)) &
            (df_filtered['rpm_range'].isin(selected_rpms)) &
            (df_filtered['bearing_type_assigned_1'].isin(top_bearings))
        ]

        fig = px.box(
            faceted,
            x='machine_type',
            y='operational_days',
            color='rpm_range',
            facet_col='bearing_type_assigned_1',
            facet_col_wrap=2,
            points='outliers',
            title="Performance Across Machines by Bearing Type"
        )
        fig.update_layout(height=800)
        st.plotly_chart(fig, use_container_width=True)

        # --- 2. Heatmap ---
        st.markdown("#### Heatmap of Average Life (Machine × Bearing)")
        heat_df = df_filtered[
            df_filtered['bearing_type_assigned_1'].isin(bearing_list)
        ]
        heat_grouped = heat_df.groupby(["bearing_type_assigned_1", "machine_type"])["operational_days"].mean().reset_index()
        pivot = heat_grouped.pivot(index="bearing_type_assigned_1", columns="machine_type", values="operational_days")
        fig = px.imshow(
            pivot,
            text_auto=True,
            aspect="auto",
            color_continuous_scale="Blues",
            labels={'color': 'Avg Operational Days'}
        )
        fig.update_layout(title="Average Operational Life (Days)", height=500)
        st.plotly_chart(fig, use_container_width=True)

        # --- 3. Scatter Plot (Mean vs Std Dev) ---
        st.markdown("#### Stability vs Performance (Mean vs Std Dev)")
        scatter_data = df_filtered.groupby(["bearing_type_assigned_1", "machine_type"])["operational_days"].agg(["mean", "std", "count"]).reset_index()
        fig = px.scatter(
            scatter_data,
            x="mean",
            y="std",
            size="count",
            color="machine_type",
            hover_data=["bearing_type_assigned_1"],
            title="Mean vs Std Dev (Higher Mean + Lower Std Dev = Better)"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

