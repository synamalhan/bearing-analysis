import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(page_title="Q18: High-RPM Failures by Industry", layout="wide")
st.markdown("<a href='/' style='text-decoration:none;'>&larr; Back to Home</a>", unsafe_allow_html=True)
st.title("Q18. Do certain industries experience more frequent high-RPM failures than others?")
st.markdown(" Explore operational stress by comparing RPM and failure frequency by sector.")

# Load data
@st.cache_data
def load_data():
    return pd.read_excel("data/Cleaned_Bearing_Dataset.xlsx")

df = load_data()

# Define RPM thresholds (customize as needed)
rpm_threshold = st.slider("Set High-RPM Threshold", min_value=1000, max_value=10000, step=500, value=3000)

# Filter failures with high RPM
df_high_rpm = df[(df["rpm_max"] >= rpm_threshold) & (df["bearing_severity_class"].notna())]

# Count high-RPM failures per industry
failures_by_industry = df_high_rpm.groupby("industry_type").size().reset_index(name="high_rpm_failure_count")
failures_by_industry = failures_by_industry.sort_values(by="high_rpm_failure_count", ascending=False)

# Plot
st.subheader(f"High-RPM Failures (RPM ≥ {rpm_threshold}) by Industry")
fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(data=failures_by_industry, x="industry_type", y="high_rpm_failure_count", palette="viridis", ax=ax)
plt.xticks(rotation=45)
plt.xlabel("Industry")
plt.ylabel("Failure Count")
plt.title(f"High-RPM Failures by Industry (RPM ≥ {rpm_threshold})")
st.pyplot(fig)

# View Data
with st.expander("View Raw Data"):
    st.dataframe(failures_by_industry)
