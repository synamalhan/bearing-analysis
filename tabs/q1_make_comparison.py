import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

def render(df=None):
    st.header("Q1: Is Make A Better Than Make B? What is the Best Make per Industry?")

    col1, col2 = st.columns([1.3, 2])

    # --- Column 1: Info ---
    with col1:
        st.subheader("Goal & Approach")
        st.markdown("""
        We aim to compare **bearing manufacturers (makes)** within each industry to determine:
        - If **Make A significantly outperforms Make B**
        - Identify the **best make per industry** by operational life

        ### Definitions & Criteria:
        - **Better Make** = Higher mean life AND statistically significant difference
        - **Statistical test** = Welch's t-test (`p < 0.05`)
        - **Practical threshold** = ≥ **15%** improvement in mean life
        - **Min. data per make** = **10 records**

        ### Assumptions:
        - We only include industries with ≥ 2 valid makes
        - Failure severity is used as a secondary tie-breaker
        """)
        with st.expander("Table Definitions"):
            st.markdown("""
            ### `make_comparison.csv`
            This table contains pairwise comparisons between makes **within each industry**.

            | Column         | Description |
            |----------------|-------------|
            | `industry`     | The industry in which the comparison is made |
            | `make_a`       | First make in the comparison |
            | `make_b`       | Second make in the comparison |
            | `mean_a`       | Average operational life of `make_a` |
            | `mean_b`       | Average operational life of `make_b` |
            | `lift_%`       | Percent improvement of `make_a` over `make_b` |
            | `p_value`      | Welch's t-test result indicating statistical significance |
            | `is_significant` | `True` if both statistically (`p < 0.05`) and practically (`lift >= 15%`) significant |

            ### `best_make_per_industry.csv`
            Summarizes the best make per industry by average operational life and failure rate.

            | Column         | Description |
            |----------------|-------------|
            | `industry`     | Industry name |
            | `best_make`    | Make with the highest average operational life (and lowest failure rate tie-breaker) |
            | `avg_life`     | Mean operational life of the best make |
            | `failure_rate` | Share of records with `severity > 0` |
            | `record_count` | Number of bearing records considered |
            """)


        with st.expander("Code: Pairwise Make Comparison"):
            st.code("""
stat, p_value = ttest_ind(a_life, b_life, equal_var=False)
lift = (a_life.mean() - b_life.mean()) / b_life.mean()
is_significant = p_value < 0.05 and lift >= 0.15
""", language="python")

        with st.expander("Code: Best Make per Industry"):
            st.code("""
make_stats = make_stats.sort_values(by=['avg_life', 'failure_rate'], ascending=[False, True])
best_make = make_stats.iloc[0]
""", language="python")

    # --- Column 2: Graphs ---
    with col2:
        st.subheader("Make A vs Make B — Lift Comparison")

        # Load comparison results
        comparison_df = pd.read_csv("exploration/outputs/q1/make_comparison.csv")

        # --- Industry Filter ---
        industries = comparison_df['industry'].unique().tolist()
        industries.sort()
        selected_industry = st.selectbox("🔍 Select an industry to view significant comparisons", options=["All"] + industries)

        if selected_industry != "All":
            filtered_df = comparison_df[comparison_df['industry'] == selected_industry]
        else:
            filtered_df = comparison_df.copy()

        # --- Scatter plot: All points (unfiltered for comparison) ---
        fig1 = px.scatter(
            comparison_df,
            x='lift_%',
            y='p_value',
            color='is_significant',
            hover_data=['industry', 'make_a', 'make_b'],
            title="Lift % vs p-value (All Industries)",
            labels={'lift_%': 'Lift (%)'}
        )
        fig1.update_yaxes(type='log', title="p-value (log scale)")
        st.plotly_chart(fig1, use_container_width=True)
        sig_df = filtered_df[filtered_df['is_significant'] == True].sort_values(by='lift_%', ascending=False)

        st.markdown("### Significant Comparisons Table")

        if not sig_df.empty:
            sig_table = sig_df[[
                'industry', 'make_a', 'make_b', 'mean_a', 'mean_b',
                'lift_%', 'p_value'
            ]].copy()

            sig_table.rename(columns={
                'industry': 'Industry',
                'make_a': 'Make A',
                'make_b': 'Make B',
                'mean_a': 'Mean Life A',
                'mean_b': 'Mean Life B',
                'lift_%': 'Lift (%)',
                'p_value': 'p-value',
            }, inplace=True)


            st.dataframe(sig_table, use_container_width=True)
        else:
            st.info("No significant comparisons to show in table.")


        st.divider()

        st.subheader("Best Make per Industry")

        # Load best make per industry
        best_df = pd.read_csv("exploration/outputs/q1/best_make_per_industry.csv")

        fig2 = px.bar(
            best_df,
            x='industry',
            y='avg_life',
            color='best_make',
            hover_data=['failure_rate', 'record_count'],
            title="Best Performing Make in Each Industry",
            labels={'avg_life': 'Avg Operational Life (days)'}
        )
        fig2.update_layout(xaxis_title="Industry", yaxis_title="Average Operational Life")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("""
        **Highlights:**
        - Each bar shows the best make in its industry with the highest average lifespan
        - Failure rate helps assess risk — a good make has both **high life** and **low failure rate**
        """)

        with st.expander("View Raw Table"):
            st.dataframe(best_df)
