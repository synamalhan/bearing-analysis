import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Q17: Failure by Bearing-Machine Pair", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q17. What is the failure distribution by bearing type and machine type combinations?")
st.markdown(" Detect which bearing–machine pairs are most prone to issues.")

# Load dataset
@st.cache_data
def load_data():
    return pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx")

df = load_data()

# Optional filters
with st.expander("Filters"):
    industry_filter = st.selectbox("Industry", ["All"] + sorted(df["industry_type"].dropna().unique()))
    if industry_filter != "All":
        df = df[df["industry_type"] == industry_filter]

# Drop rows with missing bearing/machine/failure info
df_filtered = df.dropna(subset=["bearing_type_assigned_1", "machine_type", "bearing_severity_class"])

# Group and count
grouped = df_filtered.groupby(["bearing_type_assigned_1", "machine_type"]).size().reset_index(name="count")

# Pivot for heatmap
pivot_table = grouped.pivot(index="bearing_type_assigned_1", columns="machine_type", values="count").fillna(0)

# Plot
st.subheader("Failure Distribution Heatmap")
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot_table, annot=True, fmt=".0f", cmap="Reds", ax=ax)
plt.xlabel("Machine Type")
plt.ylabel("Bearing Type")
plt.title("Failure Count by Bearing Type and Machine Type")
st.pyplot(fig)

# Raw Data Option
with st.expander(" View Raw Grouped Data"):
    st.dataframe(grouped)
