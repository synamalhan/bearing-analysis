import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q5: Is There a Typical Failure Pattern or Recommended Useful Life?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Explanation ---
    with col1:
        st.subheader("Goal and Methodology")
        st.markdown("""
        This analysis investigates whether bearing failures follow a consistent **time pattern**, enabling us to:
        - Understand **when bearings most often fail**
        - Suggest a **useful operational life threshold** (e.g., median, 75th percentile)

        ### Steps Taken:
        - Calculated **operational days** from installation to failure.
        - Plotted the **failure distribution** and **cumulative failure curve**.
        - Identified key thresholds: **Median, 75th and 90th percentiles**.

        ### Insights:
        - Bearings tend to fail most frequently within a specific operational window.
        - This window can guide **preventive replacement intervals**.
        """)

        with st.expander("Code: Calculate Useful Life"):
            st.code("""
df['operational_days'] = (df['timestamp_of_fault'] - df['subscription_start']).dt.days
median = df['operational_days'].median()
q75 = df['operational_days'].quantile(0.75)
q90 = df['operational_days'].quantile(0.9)
""", language="python")

    # --- Column 2: Graphs and Results ---
    with col2:
        st.subheader("Distribution of Operational Life")

        failure_df = pd.read_csv("exploration/outputs/q5/failure_times.csv")

        fig_hist = px.histogram(
            failure_df,
            x='operational_days',
            nbins=50,
            title="Histogram of Bearing Operational Life",
            labels={'operational_days': 'Operational Days'},
            marginal="box"
        )
        fig_hist.update_layout(bargap=0.05)
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("""
        - Shows how long bearings tend to last before failing.
        - **Right-skewed** distribution: most bearings fail early.
        """)

        st.subheader("Cumulative Failure Distribution")

        fig_cdf = px.ecdf(
            failure_df,
            x="operational_days",
            title="Cumulative Probability of Failure Over Time",
            labels={"operational_days": "Operational Days"},
        )
        st.plotly_chart(fig_cdf, use_container_width=True)

        st.markdown("""
        - **50% of bearings fail by the median lifespan.**
        - Helps identify thresholds for scheduled replacements.
        """)

        st.subheader("Recommended Useful Life Thresholds")

        life_stats = pd.read_csv("exploration/outputs/q5/useful_life_summary.csv")
        st.dataframe(life_stats, hide_index=True)

        st.markdown("""
        **Recommendations**:
        - Consider **preventive replacement** just before the 75th percentile (e.g., ~{} days)
        - Balances cost of early replacement with risk of unexpected failure
        """.format(int(life_stats.loc[life_stats['Metric'] == '75th Percentile', 'Days'].values[0])))

        st.divider()

        st.subheader("Failure Counts by Lifetime Bin")

        binned_df = pd.read_csv("exploration/outputs/q5/life_bin_summary.csv")

        fig_bin = px.bar(
            binned_df,
            x='Life Bin',
            y='Failure Count',
            title="Failure Count in Lifetime Ranges",
            labels={"Life Bin": "Operational Life Range", "Failure Count": "Number of Failures"}
        )
        fig_bin.update_layout(xaxis_title="Life Bin", yaxis_title="Failures")
        st.plotly_chart(fig_bin, use_container_width=True)

        st.markdown("""
        - Use this to identify **high-risk periods**.
        - Most failures typically concentrate in one or two life bins.
        """)

