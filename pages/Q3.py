import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Q3: Bearing Comparison Under Same Conditions", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q3: For the same asset and RPM, which bearing types perform better?")
st.markdown("""
Compare all bearing types under **identical operating conditions** — same industry, asset (machine), and RPM range.
Identify:
- Top 5 bearing types with the longest lifespan
- Bottom 5 with the shortest lifespan
""")
st.divider()

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df['operational_days'] = (df['timestamp_of_fault'] - df['subscription_start']).dt.days

    def rpm_bucket(rpm):
        if pd.isna(rpm):
            return ""
        elif rpm < 200:
            return "(0-200)"
        elif rpm < 900:
            return "(200-900)"
        elif rpm < 1500:
            return "(900-1500)"
        else:
            return "(1500+)"
    df['rpm_range'] = df['rpm_min'].apply(rpm_bucket)
    return df.dropna(subset=['operational_days'])

df = load_data()

# --- Helper: Multiselect with 'All' ---
def multiselect_with_all(label, options, default=None):
    all_label = "All"
    options = sorted(set(options))
    options_with_all = [all_label] + options

    if default is None:
        default = [all_label]

    selected = st.multiselect(label, options_with_all, default=default)

    if all_label in selected:
        return options
    return selected

# --- Filters ---
st.subheader("Select Operating Conditions")

col1, col2, col3 = st.columns(3)

with col1:
    all_industries = df['industry_type'].dropna().unique()
    selected_industries = multiselect_with_all("Select Industry Type(s)", all_industries)

with col2:
    filtered_machines_df = df[df['industry_type'].isin(selected_industries)]
    all_machines = filtered_machines_df['machine_type'].dropna().unique()
    selected_machines = multiselect_with_all("Select Machine Type(s)", all_machines)

with col3:
    all_rpms = df['rpm_range'].dropna().unique()
    selected_rpms = multiselect_with_all("Select RPM Range(s)", all_rpms)

# --- Filter Data ---
filtered_df = df[
    (df['industry_type'].isin(selected_industries)) &
    (df['machine_type'].isin(selected_machines)) &
    (df['rpm_range'].isin(selected_rpms))
]

# --- Analysis ---
if filtered_df.empty:
    st.warning("No matching data found for the selected conditions.")
else:
    grouped = filtered_df.groupby('bearing_type_assigned_1')['operational_days'].agg(
        count='count', mean='mean', median='median', std='std'
    ).reset_index()

    grouped = grouped[grouped['count'] >= 5]  # minimum data filter

    if grouped.empty:
        st.warning("Not enough data for reliable comparison.")
    else:
        top5 = grouped.nlargest(5, 'mean')
        bottom5 = grouped.nsmallest(5, 'mean')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top 5 Bearing Types by Lifespan")
            st.dataframe(top5.rename(columns={'mean': 'Avg Life (days)', 'count': 'Sample Count'}), use_container_width=True)
            fig_top = px.bar(
                top5,
                x='bearing_type_assigned_1',
                y='mean',
                error_y='std',
                color='bearing_type_assigned_1',
                labels={'bearing_type_assigned_1': 'Bearing Type', 'mean': 'Avg Life (days)'},
                title="Top 5 Bearing Types"
            )
            fig_top.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_top, use_container_width=True)

        with col2:
            st.markdown("### Bottom 5 Bearing Types by Lifespan")
            st.dataframe(bottom5.rename(columns={'mean': 'Avg Life (days)', 'count': 'Sample Count'}), use_container_width=True)
            fig_bottom = px.bar(
                bottom5,
                x='bearing_type_assigned_1',
                y='mean',
                error_y='std',
                color='bearing_type_assigned_1',
                labels={'bearing_type_assigned_1': 'Bearing Type', 'mean': 'Avg Life (days)'},
                title="Bottom 5 Bearing Types"
            )
            fig_bottom.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bottom, use_container_width=True)
