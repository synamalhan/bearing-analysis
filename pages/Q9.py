import streamlit as st
import pandas as pd
import plotly.express as px

# --- Config ---
st.set_page_config(page_title="Q9: Severity Correlation", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q9: Does Failure Severity Correlate with RPM, Machine Type, or Bearing Type?")
st.markdown("This view helps explore which combinations of features are linked with **higher severity bearing failures**.")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df = df.dropna(subset=["bearing_severity_class", "rpm_min", "bearing_type_assigned_1", "machine_type"])
    
    def rpm_bucket(rpm):
        if pd.isna(rpm):
            return "Unknown"
        elif rpm < 500:
            return "Low"
        elif rpm < 1500:
            return "Medium"
        else:
            return "High"

    df['rpm_range'] = df['rpm_min'].apply(rpm_bucket)
    return df

df = load_data()

st.divider()
tab1, tab2, tab3 = st.tabs(["By Machine Type", "By Bearing Type", "By RPM Range"])

# --- TAB 1: Machine Type Analysis ---
with tab1:
    st.subheader("Filter")
    col1, col2, col3 = st.columns(3)
    with col1:
        industry = st.selectbox("Industry", sorted(df['industry_type'].dropna().unique()), key="ind1")
    with col2:
        rpm = st.multiselect("RPM Range", ["Low", "Medium", "High"], default=["Low", "Medium", "High"], key="rpm1")
    with col3:
        bt = st.multiselect("Bearing Type", sorted(df['bearing_type_assigned_1'].dropna().unique()), key="bt1")

    df1 = df[
        (df['industry_type'] == industry) &
        (df['rpm_range'].isin(rpm)) &
        (df['bearing_type_assigned_1'].isin(bt))
    ]

    fig = px.box(df1, x="machine_type", y="bearing_severity_class", color="rpm_range",
                 title="Severity Class by Machine Type and RPM",
                 labels={"bearing_severity_class": "Severity Class", "machine_type": "Machine Type"})
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: Bearing Type Analysis ---
with tab2:
    st.subheader("Filter")
    col1, col2, col3 = st.columns(3)
    with col1:
        industry2 = st.selectbox("Industry", sorted(df['industry_type'].dropna().unique()), key="ind2")
    with col2:
        rpm2 = st.multiselect("RPM Range", ["Low", "Medium", "High"], default=["Low", "Medium", "High"], key="rpm2")
    with col3:
        machine = st.multiselect("Machine Type", sorted(df['machine_type'].dropna().unique()), key="mt2")

    df2 = df[
        (df['industry_type'] == industry2) &
        (df['rpm_range'].isin(rpm2)) &
        (df['machine_type'].isin(machine))
    ]

    fig = px.box(df2, x="bearing_type_assigned_1", y="bearing_severity_class", color="rpm_range",
                 title="Severity Class by Bearing Type and RPM",
                 labels={"bearing_severity_class": "Severity Class", "bearing_type_assigned_1": "Bearing Type"})
    fig.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 3: RPM Severity Distribution ---
with tab3:
    st.subheader("Filter")
    col1, col2 = st.columns(2)
    with col1:
        industry3 = st.selectbox("Industry", sorted(df['industry_type'].dropna().unique()), key="ind3")
    with col2:
        machine3 = st.multiselect("Machine Type", sorted(df['machine_type'].dropna().unique()), key="mt3")

    df3 = df[
        (df['industry_type'] == industry3) &
        (df['machine_type'].isin(machine3))
    ]

    fig1 = px.box(df3, x="rpm_range", y="bearing_severity_class", color="rpm_range",
                  title="Failure Severity by RPM Range",
                  labels={"bearing_severity_class": "Severity Class", "rpm_range": "RPM Range"})
    fig1.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Severity Counts by RPM")
    count_df = df3.groupby(['rpm_range', 'bearing_severity_class']).size().reset_index(name='count')
    fig2 = px.bar(count_df, x="rpm_range", y="count", color="bearing_severity_class",
                  barmode="group", title="Failure Count by RPM Range and Severity",
                  labels={"rpm_range": "RPM Range", "bearing_severity_class": "Severity Class", "count": "Failures"})
    st.plotly_chart(fig2, use_container_width=True)
