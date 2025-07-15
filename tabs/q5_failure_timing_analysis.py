
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
        - Plotted the **failure distribution**, **cumulative curve**, and **survival curve**.
        - Identified key thresholds: **Median, 75th and 90th percentiles**
        - Assessed **early failure rate**.
        """)

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

        st.subheader("Cumulative Failure Distribution")
        fig_cdf = px.ecdf(
            failure_df,
            x="operational_days",
            title="Cumulative Probability of Failure Over Time",
            labels={"operational_days": "Operational Days"},
        )
        st.plotly_chart(fig_cdf, use_container_width=True)

        st.subheader("Kaplan-Meier Survival Curve")
        surv_df = pd.read_csv("exploration/outputs/q5/survival_curve.csv")
        fig_surv = px.line(
            surv_df,
            x="operational_days",
            y="survival_probability",
            title="Kaplan-Meier Survival Curve",
            labels={"operational_days": "Operational Days", "survival_probability": "Probability of Surviving"}
        )
        fig_surv.update_layout(yaxis=dict(range=[0, 1]))
        st.plotly_chart(fig_surv, use_container_width=True)

        st.subheader("Recommended Useful Life Thresholds")
        life_stats = pd.read_csv("exploration/outputs/q5/useful_life_summary.csv")
        st.dataframe(life_stats, hide_index=True)

        median = int(life_stats.loc[life_stats['Metric'] == 'Median', 'Days'].values[0])
        q75 = int(life_stats.loc[life_stats['Metric'] == '75th Percentile', 'Days'].values[0])
        q90 = int(life_stats.loc[life_stats['Metric'] == '90th Percentile', 'Days'].values[0])

        st.markdown(f"""
        ### 📌 Recommendation:
        - Replace bearings proactively between **{q75} and {q90} days**.
        - Helps avoid unexpected failures while maximizing usage.
        """)

        st.markdown(f"""
        ### Risk Zones:
        - 🟩 **Safe Zone**: 0–{median} days  
        - 🟨 **Monitoring Zone**: {median}–{q75} days  
        - 🟥 **High Risk Zone**: {q75}+ days  
        """)

        # Early failure rate
        early_threshold = 500
        early_failures = failure_df[failure_df['operational_days'] < early_threshold]
        early_rate = len(early_failures) / len(failure_df)

        st.markdown(f"""
        ### Early Failures
        - **{early_rate * 100:.1f}%** of bearings fail within **{early_threshold} days**
        """)

        st.divider()

        st.subheader("Failure Counts by Lifetime Bin")
        binned_df = pd.read_csv("exploration/outputs/q5/life_bin_summary.csv")
        binned_df['Life Bin'] = binned_df['Life Bin'].astype(str).str.replace(",", "–").str.replace("(", "").str.replace("]", "")
        fig_bin = px.bar(
            binned_df,
            x='Life Bin',
            y='Failure Count',
            title="Failure Count in Lifetime Ranges",
            labels={"Life Bin": "Operational Life Range", "Failure Count": "Number of Failures"}
        )
        fig_bin.update_layout(xaxis_title="Life Bin", yaxis_title="Failures")
        st.plotly_chart(fig_bin, use_container_width=True)
