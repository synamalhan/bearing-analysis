# pages/Q8.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Page setup
st.set_page_config(page_title="Q8: Lubrication Method Across Industries", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q8. How does lubrication method vary across industries and machine types?")
st.markdown("Reveal industry-specific lubrication practices and their implications.")

@st.cache_data
def load_data():
    df = pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx", parse_dates=["timestamp_of_fault", "subscription_start"])
    return df

df = load_data()

# --- Optional Filters ---
with st.expander("Optional Filters"):
    industry = st.selectbox("Filter by Industry", ["All"] + sorted(df["industry_type"].dropna().unique().tolist()))
    machine = st.selectbox("Filter by Machine Type", ["All"] + sorted(df["machine_type"].dropna().unique().tolist()))

    if industry != "All":
        df = df[df["industry_type"] == industry]
    if machine != "All":
        df = df[df["machine_type"] == machine]

# --- Bar Plot: Lubrication Method Distribution ---
if "lubrication_type" in df.columns:
    lube_counts = df.groupby(["industry_type", "machine_type", "lubrication_type"]).size().reset_index(name="count")
    
    fig = px.bar(
        lube_counts,
        x="lubrication_type",
        y="count",
        color="industry_type",
        barmode="group",
        facet_col="machine_type",
        title="Lubrication Method Distribution by Industry and Machine Type",
        labels={"lubrication_type": "Lubrication Method", "count": "Count"},
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Raw Data Summary")
    st.dataframe(lube_counts)

else:
    st.error("Column `lubrication_type` not found in the dataset.")
