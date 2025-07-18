import streamlit as st
import pandas as pd
import plotly.express as px

def render(df=None):
    st.header("Q2: Is a Bearing Type Better Suited for a Specific Industry?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Info & Code ---
    with col1:
        st.subheader("Goal & Hypothesis")
        st.markdown("""
        We want to understand whether a **specific bearing type** performs better in **certain industries** than others.

        This involves checking:
        - Is there a **statistically significant difference** in bearing life across industries for each bearing type?
        - Can we **recommend ideal industries** for each bearing type based on performance?

        ### Assumptions
        - A bearing type should appear in **at least 2 industries** to be analyzed.
        - Each industry must have **≥ 5 data points** for the bearing type.
        - **Operational Life** is calculated as days between `subscription_start` and `timestamp_of_fault`.
        - We use **ANOVA** to compare means of operational life.
        """)

        with st.expander("What is ANOVA?"):
            st.markdown("""
            **ANOVA (Analysis of Variance)** is a statistical test that compares the means of multiple groups to determine if **at least one group is significantly different** from the others.

            - **Null Hypothesis (H₀)**: All group means are equal.
            - **Alternative Hypothesis (H₁)**: At least one group mean is different.
            - We use **F-statistic and p-value** to assess significance.
            - If **p < 0.05**, we reject the null and conclude the bearing behaves differently across industries.
            """)

        with st.expander("Code: ANOVA Computation"):
            st.code("""
for bearing_type in df['bearing_type_assigned_1'].unique():
    temp = df[df['bearing_type_assigned_1'] == bearing_type]
    groups = [group['operational_days'].dropna().values for _, group in temp.groupby('industry_type') if len(group) >= 5]
    if len(groups) >= 2:
        f_stat, p_val = f_oneway(*groups)
        ...
""", language='python')

        with st.expander("Table Definitions"):
            st.markdown("""
            | Column | Description |
            |--------|-------------|
            | `bearing_type` | The specific bearing identifier |
            | `num_industries` | Number of industries in which this bearing type occurs |
            | `p_value` | ANOVA test result p-value |
            | `is_significant` | `True` if p < 0.05 |
            """)

    # --- Column 2: Visual Output ---
    with col2:
        st.subheader("ANOVA Results per Bearing Type")

        anova_df = pd.read_csv("exploration/outputs/q2/anova_results.csv")

        fig1 = px.bar(
            anova_df.sort_values("p_value"),
            x="bearing_type",
            y="p_value",
            color="is_significant",
            color_discrete_map={True: "#2ca02c", False: "#d62728"},
            title="ANOVA p-values by Bearing Type"
        )
        fig1.update_layout(xaxis_title="Bearing Type", yaxis_title="p-value (log scale)")
        fig1.update_yaxes(type="log")
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("""
        - Green = Bearing type with **statistically significant differences** in lifespan across industries.
        - Red = No strong evidence that industry impacts that bearing’s life.
        """)

        st.markdown("### Full Table of ANOVA Results")
        st.dataframe(anova_df)

        # Optional filter to dive deeper into one bearing type
        st.markdown("### Explore a Specific Bearing Type")
        bearing_types = anova_df['bearing_type'].unique().tolist()
        selected_bt = st.selectbox("Select Bearing Type", options=bearing_types)

        if selected_bt and df is not None:
            filtered = df[df['bearing_type_assigned_1'] == selected_bt]

            st.markdown(f"**Industry-wise Operational Life for `{selected_bt}`**")
            fig2 = px.box(
                filtered,
                x='industry_type',
                y='operational_days',
                points='all',
                title=f"Operational Life of {selected_bt} across Industries"
            )
            fig2.update_layout(xaxis_title="Industry", yaxis_title="Operational Days")
            st.plotly_chart(fig2, use_container_width=True)

            st.markdown(f"**Failure Severity Distribution for `{selected_bt}`**")

            severity_dist = (
                filtered
                .groupby(['industry_type', 'bearing_severity_class'])
                .size()
                .reset_index(name='count')
            )
            severity_total = severity_dist.groupby('industry_type')['count'].transform('sum')
            severity_dist['percent'] = severity_dist['count'] / severity_total * 100

            fig3 = px.bar(
                severity_dist,
                x='industry_type',
                y='percent',
                color='bearing_severity_class',
                barmode='stack',
                title=f"Severity Class Distribution for {selected_bt} by Industry",
                labels={'percent': 'Percentage (%)', 'bearing_severity_class': 'Severity Class'}
            )
            fig3.update_layout(xaxis_title="Industry", yaxis_title="Share (%)")
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()
        st.subheader("📊 Visualizing Best Fits")

        st.markdown("#### Heatmap: Average Operational Days of Bearings in Each Industry")

        heatmap_df = pd.read_csv("exploration/outputs/q2/industry_bearing_heatmap.csv", index_col=0)

        fig_heatmap = px.imshow(
            heatmap_df,
            aspect="auto",
            labels=dict(x="Bearing Type", y="Industry", color="Avg Life"),
            title="Average Life of Each Bearing Type in Each Industry",
            color_continuous_scale="YlGnBu"
        )
        fig_heatmap.update_layout(height=600)
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.subheader("🔄 Best Industry per Bearing Type")

        best_industry_df = pd.read_csv("exploration/outputs/q2/best_industry_per_bearing.csv")

        st.markdown("This table shows the **best-suited industry** for each bearing type based on average lifespan.")
        st.dataframe(best_industry_df)

        fig_industry = px.bar(
            best_industry_df.sort_values("avg_operational_days", ascending=False),
            x="bearing_type_assigned_1",
            y="avg_operational_days",
            color="best_industry",
            title="Best Industry for Each Bearing Type by Avg Operational Days",
            labels={"bearing_type_assigned_1": "Bearing Type", "avg_operational_days": "Avg Life"}
        )
        fig_industry.update_layout(xaxis_title="Bearing Type", yaxis_title="Avg Life (days)")
        st.plotly_chart(fig_industry, use_container_width=True)

