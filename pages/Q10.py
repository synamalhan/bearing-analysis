import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Q10: Severity vs RPM", layout="wide", initial_sidebar_state="collapsed")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q10: Which RPM Ranges Result in Higher Failure Severity?")
st.markdown("Use this tool to explore whether **low, medium, or high RPM machines** face more severe faults.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["subscription_start", "timestamp_of_fault"])
    df = df.dropna(subset=["bearing_severity_class", "rpm_min"])
    
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

# --- Severity per RPM Range ---
st.subheader("Severity Distribution by RPM Range")

fig = px.box(df, x="rpm_range", y="bearing_severity_class", color="rpm_range",
             title="Failure Severity by RPM Range",
             labels={"bearing_severity_class": "Severity Class", "rpm_range": "RPM Range"})
fig.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig, use_container_width=True)

# --- Count Plot ---
st.subheader("Severity Class Counts within Each RPM Range")
count_df = df.groupby(['rpm_range', 'bearing_severity_class']).size().reset_index(name='count')
fig2 = px.bar(count_df, x="rpm_range", y="count", color="bearing_severity_class",
              barmode="group", title="Count of Failures by RPM and Severity Class",
              labels={"rpm_range": "RPM Range", "bearing_severity_class": "Severity Class", "count": "Number of Failures"})
st.plotly_chart(fig2, use_container_width=True)
