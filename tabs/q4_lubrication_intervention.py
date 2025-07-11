import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q4: Can Proper Lubrication Prolong Bearing Life?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Context ---
    with col1:
        st.subheader("Goal and Rationale")
        st.markdown("""
        This analysis evaluates whether the **lubrication_method** used on a bearing has a measurable impact on:
        - Its **operational lifespan**
        - Its **failure severity**

        ### Approach:
        - Operational days calculated as the difference between installation and failure.
        - Failure severity measured using the `bearing_severity_class` field (0 = no issue, 3 = severe).
        - We group and compare records by **lubrication_method**.

        ### Statistical Test:
        - **Kruskal-Wallis Test** is used to test group differences:
            - Suitable for comparing non-normally distributed lifespan and severity values
            - p-value < 0.05 indicates significant difference across groups

        ### Results:
        - **Life vs lubrication_method**: p < 0.05
        - **Severity vs lubrication_method**: p < 0.05
        - Suggests lubrication_method **does significantly affect** both lifespan and severity.
        """)

        with st.expander("Statistical Test Code"):
            st.code("""
# Kruskal-Wallis test on lifespan
groups = [g['operational_days'] for _, g in df.groupby('lubrication_method') if len(g) >= 10]
stat_life, p_life = kruskal(*groups)

# On severity
severity_groups = [g['bearing_severity_class'] for _, g in df.groupby('lubrication_method') if len(g) >= 10]
stat_sev, p_sev = kruskal(*severity_groups)
""", language="python")

        with st.expander("Definition: Kruskal-Wallis Test"):
            st.markdown("""
            A non-parametric test that compares medians across 2 or more groups.
            - Useful when data is not normally distributed.
            - It tests whether at least one group differs significantly in its central tendency.
            """)

    # --- Column 2: Visualizations and Results ---
    with col2:
        st.subheader("Summary by lubrication_method")

        # Load summary CSV
        summary_df = pd.read_csv("exploration/outputs/q4/lubrication_summary.csv")
        summary_df = summary_df.sort_values(by="avg_life", ascending=False)

        # Bar chart: Average life per method
        fig_life = px.bar(
            summary_df,
            x='lubrication_method',
            y='avg_life',
            hover_data=['count', 'median_life', 'severity_mean'],
            color='severity_mean',
            color_continuous_scale='YlGnBu',
            title="Average Bearing Life by lubrication_method",
            labels={'avg_life': 'Avg Life (days)', 'severity_mean': 'Avg Severity'}
        )
        fig_life.update_layout(xaxis_title="lubrication_method", yaxis_title="Average Operational Days")
        st.plotly_chart(fig_life, use_container_width=True)

        st.markdown("""
        - Methods with **higher average life** and **lower severity scores** indicate better lubrication practices.
        - Severity coloring provides an additional layer of insight.
        """)

        st.divider()

        st.subheader("Failure Severity Distribution")

        # Load severity class distribution data
        severity_dist = pd.read_csv("exploration/outputs/q4/lubrication_severity_distribution.csv")

        # Convert severity class to string to match color mapping keys
        severity_dist["bearing_severity_class"] = severity_dist["bearing_severity_class"].astype(str)

        # Custom color mapping from green (0) to red (3)
        severity_colors = {
            "0": "#4CAF50",  # Green
            "1": "#FFC107",  # Amber
            "2": "#FF9800",  # Orange
            "3": "#F44336"   # Red
        }

        # Bar plot using custom colors
        fig_sev = px.bar(
            severity_dist,
            x="lubrication_method",
            y="percentage",
            color="bearing_severity_class",
            color_discrete_map=severity_colors,
            barmode="stack",
            title="Failure Severity Class Distribution by Lubrication Method",
            labels={"percentage": "Percentage (%)"}
        )

        fig_sev.update_layout(yaxis_title="Percentage of Failures")
        st.plotly_chart(fig_sev, use_container_width=True)


        st.markdown("""
        - A **higher percentage of Class 0 (green)** is desirable.
        - A higher stack of **Class 3 (red)** indicates more critical failures.
        """)

        with st.expander("View Summary Table"):
            st.dataframe(summary_df)
