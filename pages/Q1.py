import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Q1: Bearing Type vs Asset Life", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q1: Bearing Type vs Asset Performance Across Assets")

# --- Load & Preprocess Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df['operational_days'] = (df['timestamp_of_fault'] - df['subscription_start']).dt.days
    df['asset_type'] = df['industry_type'] + " | " + df['machine_type'] + " | " + df['bearing_make']

    def rpm_bucket(rpm):
        if pd.isna(rpm):
            return "Unknown"
        elif rpm < 200:
            return "below 200"
        elif rpm < 900:
            return "below 900"
        elif rpm < 1500:
            return "below 1500"
        else:
            return "above 1500"
    df['rpm_range'] = df['rpm_min'].apply(rpm_bucket)
    return df.dropna(subset=['operational_days'])

df = load_data()

# --- KPIs ---
st.subheader("Key Performance Indicators")

kpi_df = df.groupby('bearing_type_assigned_1')['operational_days'].agg(['mean', 'std', 'count']).dropna()
kpi_df['cv'] = (kpi_df['std'] / kpi_df['mean']) * 100

col1, col2, col3 = st.columns(3)
with col1:
    best_avg = kpi_df['mean'].idxmax()
    st.metric("Highest Avg Life", f"{best_avg}", f"{kpi_df['mean'].max():.0f} days")

with col2:
    most_consistent = kpi_df['cv'].idxmin()
    st.metric("Most Consistent Bearing", f"{most_consistent}", f"{kpi_df['cv'].min():.1f}% CV")

with col3:
    most_data = kpi_df['count'].idxmax()
    st.metric("Most Frequent Bearing", f"{most_data}", f"{int(kpi_df['count'].max())} samples")

st.divider()

# --- Tabs ---
tab1, tab2 = st.tabs(["Fix Bearing Type → Compare Assets", "Fix Asset Attributes → Compare Bearings"])

plot_type_options = {
    "Bar Chart (Mean)": "bar",
    "Box Plot": "box",
    "Violin Plot": "violin"
}

# --- Tab 1 ---
with tab1:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Select a Bearing Type")
        selected_bearing = st.selectbox("Bearing Type", sorted(df['bearing_type_assigned_1'].dropna().unique()))
        plot_type_1 = st.radio("Plot Type", list(plot_type_options.keys()), index=0)

    with col2:
        filtered = df[df['bearing_type_assigned_1'] == selected_bearing]

        if plot_type_options[plot_type_1] == "bar":
            grouped = filtered.groupby(['asset_type', 'rpm_range']).agg(
                avg_life=('operational_days', 'mean'),
                count=('operational_days', 'count')
            ).reset_index()

            fig = px.bar(
                grouped, x='asset_type', y='avg_life', color='rpm_range',
                hover_data=['count'], title=f"Lifespan of '{selected_bearing}' Across Asset Types",
                labels={'avg_life': 'Avg Life (days)', 'asset_type': 'Asset'}
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped.rename(columns={'avg_life': 'Avg Life (days)', 'count': 'Sample Count'}))

        else:
            fig_func = px.box if plot_type_options[plot_type_1] == "box" else px.violin
            fig = fig_func(
                filtered, x='asset_type', y='operational_days', color='rpm_range',
                points="all", title=f"{plot_type_1} of '{selected_bearing}' Across Asset Types",
                labels={'asset_type': 'Asset Type', 'operational_days': 'Operational Days'}
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

            stats = filtered.groupby(['asset_type', 'rpm_range'])['operational_days'].agg(
                count='count', mean='mean', median='median', std='std'
            ).reset_index()
            st.dataframe(stats.rename(columns={'mean': 'Avg', 'median': 'Median', 'std': 'Std Dev', 'count': 'Samples'}))

# --- Tab 2 ---
with tab2:
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Fix Asset Configuration")
        query = df.copy()

        fix_industry = st.checkbox("Fix Industry Type")
        if fix_industry:
            selected_industry = st.selectbox("Industry Type", sorted(df['industry_type'].dropna().unique()))
            query = query[query['industry_type'] == selected_industry]

        fix_machine = st.checkbox("Fix Machine Type")
        if fix_machine:
            selected_machine = st.selectbox("Machine Type", sorted(query['machine_type'].dropna().unique()))
            query = query[query['machine_type'] == selected_machine]

        fix_make = st.checkbox("Fix Bearing Make")
        if fix_make:
            selected_make = st.selectbox("Bearing Make", sorted(query['bearing_make'].dropna().unique()))
            query = query[query['bearing_make'] == selected_make]

        fix_rpm = st.checkbox("Fix RPM Range")
        if fix_rpm:
            selected_rpm = st.selectbox("RPM Range", sorted(query['rpm_range'].dropna().unique()))
            query = query[query['rpm_range'] == selected_rpm]

        plot_type_2 = st.radio("Plot Type", list(plot_type_options.keys()), index=0, key="plot2")

    with col2:
        if plot_type_options[plot_type_2] == "bar":
            grouped = query.groupby(['bearing_type_assigned_1', 'rpm_range']).agg(
                avg_life=('operational_days', 'mean'),
                count=('operational_days', 'count')
            ).reset_index()

            fig = px.bar(
                grouped, x='bearing_type_assigned_1', y='avg_life', color='rpm_range',
                hover_data=['count'], title="Bearing Life by Type",
                labels={'bearing_type_assigned_1': 'Bearing Type', 'avg_life': 'Avg Life (days)'}
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(grouped.rename(columns={'avg_life': 'Avg Life (days)', 'count': 'Sample Count'}))

        else:
            fig_func = px.box if plot_type_options[plot_type_2] == "box" else px.violin
            fig = fig_func(
                query, x='bearing_type_assigned_1', y='operational_days',
                color='rpm_range' if fix_rpm else None, points="all",
                title="Distribution of Bearing Life by Type",
                labels={'bearing_type_assigned_1': 'Bearing Type', 'operational_days': 'Operational Days'}
            )
            fig.update_layout(xaxis_tickangle=-30)
            st.plotly_chart(fig, use_container_width=True)

            stats = query.groupby(
                ['bearing_type_assigned_1', 'rpm_range'] if fix_rpm else ['bearing_type_assigned_1']
            )['operational_days'].agg(
                count='count', mean='mean', median='median', std='std'
            ).reset_index()
            st.dataframe(stats.rename(columns={'mean': 'Avg', 'median': 'Median', 'std': 'Std Dev', 'count': 'Samples'}))
